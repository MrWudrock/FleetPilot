"use client";

import { useEffect, useRef, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import type { MeResponse } from "@/lib/auth";
import { fetchVehicles, syncWialon, type Vehicle } from "@/lib/fleet";

declare global {
  interface Window {
    L?: {
      map: (el: HTMLElement, opts?: object) => LeafletMap;
      tileLayer: (url: string, opts?: object) => { addTo: (map: LeafletMap) => unknown };
      layerGroup: () => {
        addTo: (map: LeafletMap) => unknown;
        clearLayers: () => void;
        addLayer: (layer: unknown) => void;
      };
      circleMarker: (
        latlng: [number, number],
        opts?: object,
      ) => {
        bindPopup: (html: string) => unknown;
        addTo: (map: unknown) => unknown;
      };
    };
  }
}

type LeafletMap = {
  setView: (latlng: [number, number], zoom: number) => LeafletMap;
  remove: () => void;
  fitBounds: (b: unknown, o?: object) => void;
};

export default function MapPage() {
  return (
    <AuthGuard>
      {(session) => <MapContent session={session} />}
    </AuthGuard>
  );
}

function MapContent({ session }: { session: MeResponse }) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<{ map: unknown; markers: unknown } | null>(null);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [filter, setFilter] = useState<"all" | "moving" | "idle" | "parked" | "offline">("all");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchVehicles();
      setVehicles(data.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    let cancelled = false;

    async function initMap() {
      if (!document.getElementById("leaflet-css")) {
        const link = document.createElement("link");
        link.id = "leaflet-css";
        link.rel = "stylesheet";
        link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
        document.head.appendChild(link);
      }

      await new Promise<void>((resolve, reject) => {
        if (window.L) {
          resolve();
          return;
        }
        const script = document.createElement("script");
        script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
        script.onload = () => resolve();
        script.onerror = () => reject(new Error("Leaflet load failed"));
        document.body.appendChild(script);
      });

      if (cancelled || !mapRef.current || !window.L) return;
      const L = window.L;

      if (!mapInstance.current) {
        const map = L.map(mapRef.current).setView([56.5, 37.0], 5);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "&copy; OpenStreetMap",
          maxZoom: 18,
        }).addTo(map);
        mapInstance.current = { map, markers: L.layerGroup().addTo(map) };
      }

      const markers = mapInstance.current.markers as {
        clearLayers: () => void;
        addLayer: (l: unknown) => void;
      };
      const map = mapInstance.current.map as { fitBounds: (b: unknown, o?: object) => void };
      markers.clearLayers();

      const filtered = vehicles.filter((v) => filter === "all" || v.motion === filter);
      const bounds: [number, number][] = [];

      for (const v of filtered) {
        if (!v.position) continue;
        const color =
          v.motion === "moving"
            ? "#059669"
            : v.motion === "idle"
              ? "#d97706"
              : v.motion === "parked"
                ? "#2563eb"
                : "#71717a";
        const marker = L.circleMarker([v.position.lat, v.position.lon], {
          radius: 8,
          color,
          fillColor: color,
          fillOpacity: 0.9,
        }).bindPopup(
          `<strong>${v.plate}</strong><br/>${v.brand ?? ""} ${v.model ?? ""}<br/>` +
            `${v.motion} · ${v.position.speed_kmh} км/ч<br/>` +
            `<span style="font-size:11px;color:#666">${v.position.source ?? ""}</span>`,
        );
        markers.addLayer(marker);
        bounds.push([v.position.lat, v.position.lon]);
      }

      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 8 });
      }
    }

    initMap().catch((e) => setError(String(e)));
    return () => {
      cancelled = true;
    };
  }, [vehicles, filter]);

  async function onSync() {
    setLoading(true);
    setError(null);
    try {
      const res = await syncWialon();
      setMessage(res.message);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sync error");
    } finally {
      setLoading(false);
    }
  }

  const counts = {
    all: vehicles.length,
    moving: vehicles.filter((v) => v.motion === "moving").length,
    idle: vehicles.filter((v) => v.motion === "idle").length,
    parked: vehicles.filter((v) => v.motion === "parked").length,
    offline: vehicles.filter((v) => v.motion === "offline").length,
  };

  return (
    <AppShell
      session={session}
      activeHref="/map"
      vehicleCount={vehicles.length}
      title="Карта автопарка"
      subtitle="Позиции из Wialon DEMO · OpenStreetMap"
      actions={
        <button
          type="button"
          disabled={loading}
          onClick={onSync}
          className="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500 disabled:opacity-60"
        >
          Sync Wialon
        </button>
      }
      mainClassName="flex flex-1 flex-col gap-3 p-4"
    >
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-700">{message}</p> : null}
      <div className="flex flex-wrap gap-2">
        {(["all", "moving", "idle", "parked", "offline"] as const).map((key) => (
          <button
            key={key}
            type="button"
            onClick={() => setFilter(key)}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              filter === key ? "bg-zinc-900 text-white" : "bg-white text-zinc-700 border border-zinc-200"
            }`}
          >
            {key} ({counts[key]})
          </button>
        ))}
      </div>
      <div ref={mapRef} className="min-h-[420px] flex-1 overflow-hidden rounded-lg border border-zinc-200 bg-zinc-200" />
      <div className="max-h-40 overflow-auto rounded-lg border border-zinc-200 bg-white">
        <table className="w-full text-left text-xs">
          <thead className="bg-zinc-50 text-zinc-500">
            <tr>
              <th className="px-3 py-2">Госномер</th>
              <th className="px-3 py-2">ТС</th>
              <th className="px-3 py-2">Статус</th>
              <th className="px-3 py-2">Скорость</th>
            </tr>
          </thead>
          <tbody>
            {vehicles
              .filter((v) => filter === "all" || v.motion === filter)
              .map((v) => (
                <tr key={v.id} className="border-t border-zinc-100">
                  <td className="px-3 py-1.5 font-medium">{v.plate}</td>
                  <td className="px-3 py-1.5">
                    {v.brand} {v.model}
                  </td>
                  <td className="px-3 py-1.5">{v.motion}</td>
                  <td className="px-3 py-1.5">{v.position?.speed_kmh ?? "—"} км/ч</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
