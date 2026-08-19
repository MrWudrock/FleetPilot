import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DISPATCHER = "dispatcher"
    FLEET_MANAGER = "fleet_manager"
    DRIVER = "driver"
    VIEWER = "viewer"


class VehicleStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class IntegrationProvider(str, enum.Enum):
    OMNICOMM = "omnicomm"
    STAVTRACK = "stavtrack"
    MSS_GLONASS = "mss_glonass"
    MASTER_TMS = "master_tms"
    ROSDOR_MONITORING = "rosdor_monitoring"
    WIALON = "wialon"
    TRANSMANAGER = "transmanager"


class IntegrationStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class OrderStatus(str, enum.Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SavingsCategory(str, enum.Enum):
    FUEL = "fuel"
    ROUTE = "route"
    DISPATCH = "dispatch"
    MAINTENANCE = "maintenance"
    PERMIT = "permit"


class PermitRequestStatus(str, enum.Enum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    READY = "ready"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    REJECTED = "rejected"


class PermitRiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MaintenanceKind(str, enum.Enum):
    TO = "to"
    REPAIR = "repair"
    INSPECTION = "inspection"


class MaintenanceStatus(str, enum.Enum):
    PLANNED = "planned"
    OVERDUE = "overdue"
    IN_PROGRESS = "in_progress"
    DONE = "done"
