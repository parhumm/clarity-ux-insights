"""Configuration loader for Clarity UX Insights."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
    """Project configuration."""
    name: str = "Clarity Project"
    type: str = "website"
    url: Optional[str] = None


@dataclass
class ClarityAPIConfig:
    """Clarity API configuration."""
    default_dimensions: List[str] = field(default_factory=lambda: ["Device", "Country", "Browser"])
    api_rate_limit: int = 10
    timeout_seconds: int = 30


@dataclass
class PageTrackingConfig:
    """Page tracking configuration."""
    id: str
    path: str
    name: str
    category: str = "general"


@dataclass
class TrackingConfig:
    """Tracking configuration."""
    pages: List[PageTrackingConfig] = field(default_factory=list)
    auto_track_patterns: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class DataConfig:
    """Data management configuration."""
    retention_days: int = 90
    auto_cleanup: bool = True
    max_storage_gb: int = 10
    compress_archives: bool = True


@dataclass
class ReportsConfig:
    """Report generation configuration."""
    default_period_days: int = 3
    generate_on_fetch: bool = True
    output_formats: List[str] = field(default_factory=lambda: ["markdown", "csv"])
    auto_generate: List[str] = field(default_factory=lambda: ["ux-health"])
    archive_reports_after_days: int = 90


@dataclass
class NotificationsConfig:
    """Notifications configuration."""
    enabled: bool = False
    email: Optional[str] = None
    alert_on_high_frustration: bool = False
    frustration_threshold: float = 20.0


@dataclass
class ClarityConfig:
    """Complete Clarity configuration."""
    project: ProjectConfig = field(default_factory=ProjectConfig)
    clarity: ClarityAPIConfig = field(default_factory=ClarityAPIConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    reports: ReportsConfig = field(default_factory=ReportsConfig)
    notifications: NotificationsConfig = field(default_factory=NotificationsConfig)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'ClarityConfig':
        """Load configuration from YAML file.

        Args:
            config_path: Path to config.yaml. If None, looks in config/config.yaml

        Returns:
            ClarityConfig instance with loaded settings
        """
        if config_path is None:
            # Try multiple locations
            possible_paths = [
                Path(__file__).parent / "config.yaml",
                Path("config.yaml"),
            ]
            config_path = None
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break

        if config_path is None or not config_path.exists():
            print("⚠️  No config.yaml found. Using default configuration.")
            print("💡 Copy config/config.template.yaml to config/config.yaml to customize.")
            return cls()

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}

        # Parse configuration sections
        project = cls._parse_project(data.get('project', {}))
        clarity_api = cls._parse_clarity(data.get('clarity', {}))
        tracking = cls._parse_tracking(data.get('tracking', {}))
        data_config = cls._parse_data(data.get('data', {}))
        reports = cls._parse_reports(data.get('reports', {}))
        notifications = cls._parse_notifications(data.get('notifications', {}))

        return cls(
            project=project,
            clarity=clarity_api,
            tracking=tracking,
            data=data_config,
            reports=reports,
            notifications=notifications
        )

    @staticmethod
    def _parse_project(data: Dict) -> ProjectConfig:
        """Parse project configuration."""
        return ProjectConfig(
            name=data.get('name', 'Clarity Project'),
            type=data.get('type', 'website'),
            url=data.get('url')
        )

    @staticmethod
    def _parse_clarity(data: Dict) -> ClarityAPIConfig:
        """Parse Clarity API configuration."""
        return ClarityAPIConfig(
            default_dimensions=data.get('default_dimensions', ["Device", "Country", "Browser"]),
            api_rate_limit=data.get('api_rate_limit', 10),
            timeout_seconds=data.get('timeout_seconds', 30)
        )

    @staticmethod
    def _parse_tracking(data: Dict) -> TrackingConfig:
        """Parse tracking configuration."""
        pages_data = data.get('pages', [])
        pages = [
            PageTrackingConfig(
                id=p['id'],
                path=p['path'],
                name=p['name'],
                category=p.get('category', 'general')
            )
            for p in pages_data
        ] if pages_data else []

        return TrackingConfig(
            pages=pages,
            auto_track_patterns=data.get('auto_track_patterns', [])
        )

    @staticmethod
    def _parse_data(data: Dict) -> DataConfig:
        """Parse data management configuration."""
        return DataConfig(
            retention_days=data.get('retention_days', 90),
            auto_cleanup=data.get('auto_cleanup', True),
            max_storage_gb=data.get('max_storage_gb', 10),
            compress_archives=data.get('compress_archives', True)
        )

    @staticmethod
    def _parse_reports(data: Dict) -> ReportsConfig:
        """Parse reports configuration."""
        return ReportsConfig(
            default_period_days=data.get('default_period_days', 3),
            generate_on_fetch=data.get('generate_on_fetch', True),
            output_formats=data.get('output_formats', ['markdown', 'csv']),
            auto_generate=data.get('auto_generate', ['ux-health']),
            archive_reports_after_days=data.get('archive_reports_after_days', 90)
        )

    @staticmethod
    def _parse_notifications(data: Dict) -> NotificationsConfig:
        """Parse notifications configuration."""
        return NotificationsConfig(
            enabled=data.get('enabled', False),
            email=data.get('email'),
            alert_on_high_frustration=data.get('alert_on_high_frustration', False),
            frustration_threshold=data.get('frustration_threshold', 20.0)
        )

    def get_page_by_id(self, page_id: str) -> Optional[PageTrackingConfig]:
        """Get page configuration by ID."""
        for page in self.tracking.pages:
            if page.id == page_id:
                return page
        return None

    def get_page_by_path(self, path: str) -> Optional[PageTrackingConfig]:
        """Get page configuration by path."""
        for page in self.tracking.pages:
            if page.path == path:
                return page
        return None

    def get_pages_by_category(self, category: str) -> List[PageTrackingConfig]:
        """Get all pages in a category."""
        return [p for p in self.tracking.pages if p.category == category]

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Validate project
        if not self.project.name:
            errors.append("Project name is required")

        # Validate page IDs are unique
        page_ids = [p.id for p in self.tracking.pages]
        if len(page_ids) != len(set(page_ids)):
            errors.append("Duplicate page IDs found in tracking configuration")

        # Validate page paths are unique
        page_paths = [p.path for p in self.tracking.pages]
        if len(page_paths) != len(set(page_paths)):
            errors.append("Duplicate page paths found in tracking configuration")

        # Validate output formats
        valid_formats = ['markdown', 'csv', 'json']
        for fmt in self.reports.output_formats:
            if fmt not in valid_formats:
                errors.append(f"Invalid output format: {fmt}. Valid: {valid_formats}")

        return errors


def load_config(config_path: Optional[Path] = None) -> ClarityConfig:
    """Convenience function to load configuration.

    Args:
        config_path: Path to config.yaml

    Returns:
        ClarityConfig instance
    """
    config = ClarityConfig.load(config_path)

    # Validate configuration
    errors = config.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        raise ValueError("Invalid configuration")

    return config


if __name__ == "__main__":
    # Test configuration loading
    print("Testing configuration loader...")

    config = load_config()
    print(f"\n✓ Configuration loaded:")
    print(f"  - Project: {config.project.name} ({config.project.type})")
    print(f"  - Pages tracked: {len(config.tracking.pages)}")
    print(f"  - Default period: {config.reports.default_period_days} days")
    print(f"  - Output formats: {', '.join(config.reports.output_formats)}")
    print(f"  - Retention: {config.data.retention_days} days")
