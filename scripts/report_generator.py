#!/usr/bin/env python3
"""
Database-driven report generator using universal templates.
"""

import sqlite3
import yaml
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.query_engine import QueryEngine, DateRange, DateParser
from config_loader import load_config


class ReportGenerator:
    """Generate reports from database using universal templates."""

    def __init__(self):
        """Initialize report generator."""
        self.query_engine = QueryEngine()
        try:
            self.config = load_config()
        except:
            self.config = None

        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.reports_dir = Path(__file__).parent.parent / "reports"

    def generate_report(
        self,
        template_name: str,
        date_range: DateRange,
        output_path: Optional[Path] = None,
        page_id: Optional[str] = None
    ) -> Path:
        """
        Generate a report from a template.

        Args:
            template_name: Name of template (e.g., 'ux-health', 'frustration-analysis')
            date_range: Date range to generate report for
            output_path: Optional custom output path
            page_id: Optional page ID for page-specific reports

        Returns:
            Path to generated report
        """
        # Load template
        template_path = self._find_template(template_name)
        with open(template_path, 'r') as f:
            template_content = f.read()

        # Extract YAML frontmatter
        frontmatter, template_body = self._extract_frontmatter(template_content)

        # Gather data from database
        data = self._gather_data(date_range, page_id)

        # Fill placeholders
        report_content = self._fill_placeholders(
            template_body,
            data,
            date_range,
            page_id
        )

        # Update frontmatter with actual values
        frontmatter_filled = self._fill_placeholders(
            yaml.dump(frontmatter),
            data,
            date_range,
            page_id
        )

        # Combine frontmatter and body
        final_report = f"---\n{frontmatter_filled}---\n\n{report_content}"

        # Determine output path
        if output_path is None:
            output_path = self._default_output_path(
                template_name,
                date_range,
                page_id
            )

        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(final_report)

        return output_path

    def _find_template(self, template_name: str) -> Path:
        """Find template file by name."""
        # Try general templates
        general_path = self.templates_dir / "general" / f"{template_name}.md.template"
        if general_path.exists():
            return general_path

        # Try page templates
        page_path = self.templates_dir / "pages" / f"{template_name}.md.template"
        if page_path.exists():
            return page_path

        raise FileNotFoundError(f"Template not found: {template_name}")

    def _extract_frontmatter(self, content: str) -> tuple:
        """Extract YAML frontmatter from template."""
        if not content.startswith("---"):
            return {}, content

        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content

        try:
            frontmatter = yaml.safe_load(parts[1])
            if frontmatter is None:
                frontmatter = {}
        except:
            frontmatter = {}

        return frontmatter, parts[2]

    def _gather_data(
        self,
        date_range: DateRange,
        page_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gather all data needed for report."""
        data = {}

        # Query general traffic metrics
        traffic_metrics = self.query_engine.query_metrics(
            date_range,
            metric_name="Traffic",
            data_scope="general"
        )

        # Query individual frustration metrics (Clarity stores them separately)
        dead_clicks_metrics = self.query_engine.query_metrics(
            date_range,
            metric_name="DeadClickCount",
            data_scope="general"
        )

        rage_clicks_metrics = self.query_engine.query_metrics(
            date_range,
            metric_name="RageClickCount",
            data_scope="general"
        )

        quick_backs_metrics = self.query_engine.query_metrics(
            date_range,
            metric_name="QuickbackClick",
            data_scope="general"
        )

        error_clicks_metrics = self.query_engine.query_metrics(
            date_range,
            metric_name="ErrorClickCount",
            data_scope="general"
        )

        script_errors_metrics = self.query_engine.query_metrics(
            date_range,
            metric_name="ScriptErrorCount",
            data_scope="general"
        )

        # Query individual engagement metrics
        engagement_time_metrics = self.query_engine.query_metrics(
            date_range,
            metric_name="EngagementTime",
            data_scope="general"
        )

        scroll_depth_metrics = self.query_engine.query_metrics(
            date_range,
            metric_name="ScrollDepth",
            data_scope="general"
        )

        # Aggregate traffic data
        if traffic_metrics:
            data.update(self._aggregate_traffic(traffic_metrics))

        # Aggregate frustration data from individual metrics
        frustration_data = self._aggregate_frustration(
            dead_clicks_metrics,
            rage_clicks_metrics,
            quick_backs_metrics,
            error_clicks_metrics,
            script_errors_metrics,
            traffic_metrics
        )
        data.update(frustration_data)

        # Aggregate engagement data
        engagement_data = self._aggregate_engagement(
            engagement_time_metrics,
            scroll_depth_metrics,
            traffic_metrics
        )
        data.update(engagement_data)

        # Page-specific data
        if page_id:
            page_data = self._gather_page_data(date_range, page_id)
            data.update(page_data)

        return data

    def _aggregate_traffic(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Aggregate traffic metrics."""
        if not metrics:
            return {}

        total_sessions = sum(m.get('sessions') or 0 for m in metrics)
        total_users = sum(m.get('users') or 0 for m in metrics)
        total_page_views = sum(m.get('page_views') or 0 for m in metrics)
        bot_sessions = sum(m.get('bot_sessions') or 0 for m in metrics)

        # Device breakdown
        mobile = sum(m.get('mobile_sessions') or 0 for m in metrics)
        desktop = sum(m.get('desktop_sessions') or 0 for m in metrics)
        tablet = sum(m.get('tablet_sessions') or 0 for m in metrics)

        return {
            'TOTAL_SESSIONS': f"{total_sessions:,}",
            'UNIQUE_USERS': f"{total_users:,}",  # Renamed from TOTAL_USERS
            'TOTAL_USERS': f"{total_users:,}",  # Keep for backward compatibility
            'TOTAL_PAGE_VIEWS': f"{total_page_views:,}",
            'BOT_SESSIONS': f"{bot_sessions:,}",
            'BOT_PERCENTAGE': f"{(bot_sessions/total_sessions*100 if total_sessions else 0):.1f}",
            'MOBILE_SESSIONS': f"{mobile:,}",
            'DESKTOP_SESSIONS': f"{desktop:,}",
            'TABLET_SESSIONS': f"{tablet:,}",
            'MOBILE_PERCENTAGE': f"{(mobile/total_sessions*100 if total_sessions else 0):.1f}",
            'DESKTOP_PERCENTAGE': f"{(desktop/total_sessions*100 if total_sessions else 0):.1f}",
            'TABLET_PERCENTAGE': f"{(tablet/total_sessions*100 if total_sessions else 0):.1f}",
            'AVG_SESSION_DURATION': self._format_duration(
                sum(m.get('total_session_time', 0) for m in metrics) / total_sessions if total_sessions else 0
            ),
        }

    def _aggregate_frustration(
        self,
        dead_clicks_metrics: List[Dict],
        rage_clicks_metrics: List[Dict],
        quick_backs_metrics: List[Dict],
        error_clicks_metrics: List[Dict],
        script_errors_metrics: List[Dict],
        traffic_metrics: List[Dict]
    ) -> Dict[str, Any]:
        """Aggregate frustration metrics from individual Clarity metric types."""
        # Get session count from traffic metrics
        total_sessions = sum(m.get('sessions') or 0 for m in traffic_metrics) if traffic_metrics else 0

        # Aggregate each frustration type
        dead_clicks = sum(m.get('dead_clicks') or 0 for m in dead_clicks_metrics) if dead_clicks_metrics else 0
        rage_clicks = sum(m.get('rage_clicks') or 0 for m in rage_clicks_metrics) if rage_clicks_metrics else 0
        quick_backs = sum(m.get('quick_backs') or 0 for m in quick_backs_metrics) if quick_backs_metrics else 0
        error_clicks = sum(m.get('error_clicks') or 0 for m in error_clicks_metrics) if error_clicks_metrics else 0
        script_errors = sum(m.get('script_errors') or 0 for m in script_errors_metrics) if script_errors_metrics else 0

        total_frustration = dead_clicks + rage_clicks + quick_backs + error_clicks

        return {
            'TOTAL_DEAD_CLICKS': f"{dead_clicks:,}",
            'TOTAL_RAGE_CLICKS': f"{rage_clicks:,}",
            'TOTAL_QUICK_BACKS': f"{quick_backs:,}",
            'TOTAL_ERROR_CLICKS': f"{error_clicks:,}",
            'TOTAL_SCRIPT_ERRORS': f"{script_errors:,}",
            'TOTAL_FRUSTRATION_SIGNALS': f"{total_frustration:,}",
            'DEAD_CLICK_RATE': f"{(dead_clicks/total_sessions*100 if total_sessions else 0):.1f}",
            'RAGE_CLICK_RATE': f"{(rage_clicks/total_sessions*100 if total_sessions else 0):.1f}",
            'QUICK_BACK_RATE': f"{(quick_backs/total_sessions*100 if total_sessions else 0):.1f}",
            'ERROR_CLICK_RATE': f"{(error_clicks/total_sessions*100 if total_sessions else 0):.1f}",
            'SCRIPT_ERROR_RATE': f"{(script_errors/total_sessions*100 if total_sessions else 0):.1f}",
            'FRUSTRATION_RATE': f"{(total_frustration/total_sessions if total_sessions else 0):.2f}",
        }

    def _aggregate_engagement(
        self,
        engagement_time_metrics: List[Dict],
        scroll_depth_metrics: List[Dict],
        traffic_metrics: List[Dict]
    ) -> Dict[str, Any]:
        """Aggregate engagement metrics from individual Clarity metric types."""
        # Get session count from traffic metrics
        total_sessions = sum(m.get('sessions') or 0 for m in traffic_metrics) if traffic_metrics else 0

        # Aggregate scroll depth
        total_scroll = sum(m.get('scroll_depth') or 0 for m in scroll_depth_metrics) if scroll_depth_metrics else 0
        scroll_count = len([m for m in scroll_depth_metrics if m.get('scroll_depth')]) if scroll_depth_metrics else 0
        avg_scroll_depth = (total_scroll / scroll_count) if scroll_count > 0 else 0

        # Aggregate engagement time
        total_engagement = sum(m.get('engagement_time') or 0 for m in engagement_time_metrics) if engagement_time_metrics else 0
        engagement_count = len([m for m in engagement_time_metrics if m.get('engagement_time')]) if engagement_time_metrics else 0
        avg_engagement_time = (total_engagement / engagement_count) if engagement_count > 0 else 0

        return {
            'AVG_SCROLL_DEPTH': f"{avg_scroll_depth:.1f}",
            'AVG_ENGAGEMENT_TIME': f"{avg_engagement_time:.0f}",
            'AVG_TIME_ON_PAGE': self._format_duration(avg_engagement_time),
            'AVG_ACTIVE_TIME': self._format_duration(avg_engagement_time * 0.7),  # Estimate active time as 70% of engagement
        }

    def _gather_page_data(self, date_range: DateRange, page_id: str) -> Dict[str, Any]:
        """Gather page-specific data."""
        # Query page metrics
        page_metrics = self.query_engine.query_metrics(
            date_range,
            data_scope="page",
            page_id=page_id
        )

        data = {'PAGE_ID': page_id}

        if page_metrics:
            # Aggregate page data
            total_sessions = sum(m.get('sessions', 0) for m in page_metrics)
            data['PAGE_SESSIONS'] = f"{total_sessions:,}"

        return data

    def _fill_placeholders(
        self,
        template: str,
        data: Dict[str, Any],
        date_range: DateRange,
        page_id: Optional[str] = None
    ) -> str:
        """Fill template placeholders with data."""
        content = template

        # Project info
        if self.config:
            content = content.replace('{PROJECT_NAME}', self.config.project.name)
            content = content.replace('{PROJECT_TYPE}', self.config.project.type)
            content = content.replace('{PROJECT_URL}', self.config.project.url or 'N/A')
        else:
            content = content.replace('{PROJECT_NAME}', 'My Project')
            content = content.replace('{PROJECT_TYPE}', 'website')
            content = content.replace('{PROJECT_URL}', 'N/A')

        # Date range and period
        period_days = (date_range.end - date_range.start).days + 1
        content = content.replace('{START_DATE}', date_range.start.isoformat())
        content = content.replace('{END_DATE}', date_range.end.isoformat())
        content = content.replace('{PERIOD_DAYS}', str(period_days))
        content = content.replace('{GENERATED_DATE}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        content = content.replace('{REPORT_GENERATION_DATE}', datetime.now().isoformat())

        # Page info
        if page_id:
            content = content.replace('{PAGE_ID}', page_id)

        # Data placeholders
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))

        # Calculate health scores and trends
        health_data = self._calculate_health_score(data)
        data.update(health_data)

        trend_data = self._calculate_trends(date_range, data)
        data.update(trend_data)

        # Fill calculated placeholders
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))

        # Generate insights (placeholder for now)
        content = self._generate_insights(content, data)

        return content

    def _calculate_health_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate UX health score and issue counts."""
        # Extract numeric values from formatted strings
        def extract_num(val_str):
            if isinstance(val_str, str):
                return float(val_str.replace(',', '').replace('%', ''))
            return float(val_str) if val_str else 0

        dead_click_rate = extract_num(data.get('DEAD_CLICK_RATE', '0'))
        rage_click_rate = extract_num(data.get('RAGE_CLICK_RATE', '0'))
        quick_back_rate = extract_num(data.get('QUICK_BACK_RATE', '0'))
        error_click_rate = extract_num(data.get('ERROR_CLICK_RATE', '0'))
        script_error_rate = extract_num(data.get('SCRIPT_ERROR_RATE', '0'))

        # Count critical issues (thresholds based on industry standards)
        critical_issues = 0
        warnings = 0
        good_signals = 0

        # Dead clicks: critical if >5%, warning if >2%
        if dead_click_rate > 5:
            critical_issues += 1
        elif dead_click_rate > 2:
            warnings += 1
        else:
            good_signals += 1

        # Rage clicks: critical if >1%, warning if >0.5%
        if rage_click_rate > 1:
            critical_issues += 1
        elif rage_click_rate > 0.5:
            warnings += 1
        else:
            good_signals += 1

        # Quick backs: critical if >10%, warning if >5%
        if quick_back_rate > 10:
            critical_issues += 1
        elif quick_back_rate > 5:
            warnings += 1
        else:
            good_signals += 1

        # Error clicks: critical if >1%, warning if >0%
        if error_click_rate > 1:
            critical_issues += 1
        elif error_click_rate > 0:
            warnings += 1
        else:
            good_signals += 1

        # Script errors: critical if >0.5%, warning if >0%
        if script_error_rate > 0.5:
            critical_issues += 1
        elif script_error_rate > 0:
            warnings += 1
        else:
            good_signals += 1

        # Calculate overall health score (0-100)
        # Start at 100, deduct points for issues
        score = 100
        score -= critical_issues * 15  # -15 per critical issue
        score -= warnings * 7  # -7 per warning
        score = max(0, score)  # Don't go below 0

        # Health indicator
        if score >= 80:
            indicator = "🟢 Excellent"
        elif score >= 60:
            indicator = "🟡 Good"
        elif score >= 40:
            indicator = "🟠 Fair"
        else:
            indicator = "🔴 Needs Attention"

        return {
            'UX_HEALTH_SCORE': str(score),
            'HEALTH_INDICATOR': indicator,
            'CRITICAL_ISSUES_COUNT': str(critical_issues),
            'WARNINGS_COUNT': str(warnings),
            'GOOD_SIGNALS_COUNT': str(good_signals),
        }

    def _calculate_trends(self, date_range: DateRange, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate trend indicators by comparing to previous period."""
        # Calculate previous period (same length as current)
        period_length = (date_range.end - date_range.start).days + 1
        from datetime import timedelta
        prev_end = date_range.start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_length - 1)
        prev_range = DateRange(prev_start, prev_end)

        # Try to get previous period data
        try:
            prev_data = self._gather_data(prev_range)
        except:
            # If no previous data, return neutral trends
            return {
                'SESSIONS_TREND': '→',
                'USERS_TREND': '→',
                'DEAD_CLICK_TREND': '→',
                'RAGE_CLICK_TREND': '→',
                'QUICK_BACK_TREND': '→',
                'SCROLL_DEPTH_TREND': '→',
                'ENGAGEMENT_TREND': '→',
            }

        def extract_num(val_str):
            if isinstance(val_str, str):
                return float(val_str.replace(',', '').replace('%', ''))
            return float(val_str) if val_str else 0

        def calc_trend(current_val, prev_val, higher_is_better=True):
            """Calculate trend indicator."""
            curr = extract_num(current_val)
            prev = extract_num(prev_val)
            if prev == 0:
                return '→'
            change_pct = ((curr - prev) / prev) * 100
            if abs(change_pct) < 5:  # Less than 5% change is neutral
                return '→'
            if higher_is_better:
                return '↑' if change_pct > 0 else '↓'
            else:
                return '↓' if change_pct > 0 else '↑'  # Inverted for frustration metrics

        return {
            'SESSIONS_TREND': calc_trend(current_data.get('TOTAL_SESSIONS', '0'), prev_data.get('TOTAL_SESSIONS', '0'), True),
            'USERS_TREND': calc_trend(current_data.get('UNIQUE_USERS', '0'), prev_data.get('UNIQUE_USERS', '0'), True),
            'DEAD_CLICK_TREND': calc_trend(current_data.get('DEAD_CLICK_RATE', '0'), prev_data.get('DEAD_CLICK_RATE', '0'), False),
            'RAGE_CLICK_TREND': calc_trend(current_data.get('RAGE_CLICK_RATE', '0'), prev_data.get('RAGE_CLICK_RATE', '0'), False),
            'QUICK_BACK_TREND': calc_trend(current_data.get('QUICK_BACK_RATE', '0'), prev_data.get('QUICK_BACK_RATE', '0'), False),
            'SCROLL_DEPTH_TREND': calc_trend(current_data.get('AVG_SCROLL_DEPTH', '0'), prev_data.get('AVG_SCROLL_DEPTH', '0'), True),
            'ENGAGEMENT_TREND': calc_trend(current_data.get('AVG_ENGAGEMENT_TIME', '0'), prev_data.get('AVG_ENGAGEMENT_TIME', '0'), True),
        }

    def _generate_insights(self, content: str, data: Dict[str, Any]) -> str:
        """Generate audience-specific insights."""
        # For now, use placeholder text
        # In a real implementation, this would use AI or rule-based logic

        insights = {
            'TECHNICAL_INSIGHTS': '- Review high frustration signals\n- Optimize slow-loading pages\n- Fix error-prone interactions',
            'UX_INSIGHTS': '- Improve mobile experience\n- Reduce friction points\n- Enhance engagement metrics',
            'BUSINESS_INSIGHTS': '- User engagement trending positively\n- Mobile traffic dominates\n- Focus on conversion optimization',
            'MARKETING_INSIGHTS': '- Strong mobile presence\n- Geographic diversity\n- Optimize for peak traffic times',
            'KEY_FINDINGS': '- Mobile-first audience\n- High engagement metrics\n- Some frustration signals to address',
            'RECOMMENDATIONS': '- Fix identified frustration points\n- Optimize mobile experience\n- Monitor key metrics weekly',
            'NEXT_STEPS': '- Implement recommended fixes\n- A/B test improvements\n- Continue monitoring',
        }

        for key, value in insights.items():
            content = content.replace(f"{{{key}}}", value)

        return content

    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable format."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"

    def _default_output_path(
        self,
        template_name: str,
        date_range: DateRange,
        page_id: Optional[str] = None
    ) -> Path:
        """Generate default output path for report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        date_str = f"{date_range.start.isoformat()}_to_{date_range.end.isoformat()}"

        if page_id:
            # Page-specific report
            # Sanitize page_id for filesystem (remove leading slash, replace / with _)
            safe_page_id = page_id.lstrip('/').replace('/', '_')
            filename = f"{template_name}_{safe_page_id}_{date_str}_{timestamp}.md"
            return self.reports_dir / "pages" / safe_page_id / filename
        else:
            # General report
            filename = f"{template_name}_{date_str}_{timestamp}.md"
            return self.reports_dir / "general" / filename


def main():
    """CLI interface for report generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate reports from database")
    parser.add_argument('template', help='Template name (e.g., ux-health, frustration-analysis)')
    parser.add_argument('date_range', help='Date range (e.g., 7, last-week, November)')
    parser.add_argument('--page', help='Page ID for page-specific reports')
    parser.add_argument('--output', help='Custom output path')

    args = parser.parse_args()

    # Parse date range
    date_range = DateParser.parse(args.date_range)

    # Generate report
    generator = ReportGenerator()
    output_path = generator.generate_report(
        args.template,
        date_range,
        output_path=Path(args.output) if args.output else None,
        page_id=args.page
    )

    print(f"✓ Report generated: {output_path}")


if __name__ == "__main__":
    main()
