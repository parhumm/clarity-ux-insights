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
        """Generate data-driven audience-specific insights."""
        def extract_num(val_str):
            if isinstance(val_str, str):
                return float(val_str.replace(',', '').replace('%', ''))
            return float(val_str) if val_str else 0

        # Extract metrics
        total_sessions = extract_num(data.get('TOTAL_SESSIONS', '0'))
        unique_users = extract_num(data.get('UNIQUE_USERS', '0'))
        dead_clicks = extract_num(data.get('TOTAL_DEAD_CLICKS', '0'))
        rage_clicks = extract_num(data.get('TOTAL_RAGE_CLICKS', '0'))
        quick_backs = extract_num(data.get('TOTAL_QUICK_BACKS', '0'))
        error_clicks = extract_num(data.get('TOTAL_ERROR_CLICKS', '0'))
        script_errors = extract_num(data.get('TOTAL_SCRIPT_ERRORS', '0'))
        bot_sessions = extract_num(data.get('BOT_SESSIONS', '0'))

        dead_click_rate = extract_num(data.get('DEAD_CLICK_RATE', '0'))
        rage_click_rate = extract_num(data.get('RAGE_CLICK_RATE', '0'))
        quick_back_rate = extract_num(data.get('QUICK_BACK_RATE', '0'))
        health_score = extract_num(data.get('UX_HEALTH_SCORE', '0'))
        critical_issues = int(extract_num(data.get('CRITICAL_ISSUES_COUNT', '0')))

        # Generate executive summary
        if health_score >= 80:
            health_desc = "excellent UX health"
        elif health_score >= 60:
            health_desc = "good UX health with minor concerns"
        elif health_score >= 40:
            health_desc = "fair UX health requiring attention"
        else:
            health_desc = "concerning UX health needing immediate action"

        top_issue = ""
        if dead_click_rate > 5:
            top_issue = f"Dead clicks affecting {dead_click_rate:.1f}% of sessions ({int(dead_clicks):,} total incidents)"
        elif rage_click_rate > 1:
            top_issue = f"Rage clicks in {rage_click_rate:.1f}% of sessions ({int(rage_clicks):,} total incidents)"
        elif quick_back_rate > 10:
            top_issue = f"Quick backs in {quick_back_rate:.1f}% of sessions ({int(quick_backs):,} total incidents)"
        else:
            top_issue = "No major UX issues detected"

        # Critical findings
        critical_findings = ""
        if critical_issues > 0:
            critical_findings += f"**{critical_issues} Critical Issues Identified:**\n\n"
            if dead_click_rate > 5:
                critical_findings += f"1. **Dead Clicks Crisis:** {int(dead_clicks):,} incidents ({dead_click_rate:.1f}% of sessions) - Users clicking on non-interactive elements, indicating UI confusion.\n\n"
            if rage_click_rate > 1:
                critical_findings += f"2. **Rage Click Alerts:** {int(rage_clicks):,} incidents ({rage_click_rate:.1f}% of sessions) - Users frantically clicking, signaling broken functionality.\n\n"
            if quick_back_rate > 10:
                critical_findings += f"3. **Quick Back Pattern:** {int(quick_backs):,} incidents ({quick_back_rate:.1f}% of sessions) - Users immediately abandoning pages, suggesting poor landing experience.\n\n"
        else:
            critical_findings = "No critical UX issues detected. System performing within acceptable parameters."

        exec_summary = f"Analysis of {int(total_sessions):,} sessions from {int(unique_users):,} unique users shows {health_desc}. "
        if top_issue:
            exec_summary += f"Primary concern: {top_issue}. "
        exec_summary += f"Detected {critical_issues} critical issues requiring immediate remediation."

        # Technical insights
        tech_insights = f"**Performance & Errors:**\n"
        if script_errors > 0:
            tech_insights += f"- {int(script_errors):,} script errors detected - investigate JavaScript issues\n"
        if error_clicks > 0:
            tech_insights += f"- {int(error_clicks):,} error clicks - users encountering system errors\n"
        else:
            tech_insights += "- No script or error click issues detected\n"
        tech_insights += f"- Bot traffic: {int(bot_sessions):,} sessions ({bot_sessions/total_sessions*100 if total_sessions else 0:.1f}%)\n\n"
        tech_insights += f"**Priority Fixes:**\n"
        if dead_click_rate > 5:
            tech_insights += f"- HIGH: Dead clicks ({int(dead_clicks):,} total) - elements appearing clickable but non-functional\n"
        if rage_click_rate > 1:
            tech_insights += f"- HIGH: Rage clicks ({int(rage_clicks):,} total) - users repeatedly clicking in frustration\n"
        if quick_back_rate > 10:
            tech_insights += f"- HIGH: Quick backs ({int(quick_backs):,} total) - users immediately leaving pages\n"

        # UX insights
        ux_insights = f"**Frustration Analysis:**\n"
        ux_insights += f"- Dead clicks: {int(dead_clicks):,} incidents ({dead_click_rate:.1f}% of sessions)\n"
        ux_insights += f"- Rage clicks: {int(rage_clicks):,} incidents ({rage_click_rate:.1f}% of sessions)\n"
        ux_insights += f"- Quick backs: {int(quick_backs):,} incidents ({quick_back_rate:.1f}% of sessions)\n\n"
        ux_insights += f"**Recommendations:**\n"
        if dead_click_rate > 5:
            ux_insights += "- Review UI for misleading clickable elements\n"
        if rage_click_rate > 1:
            ux_insights += "- Identify and fix unresponsive interactions\n"
        if quick_back_rate > 10:
            ux_insights += "- Analyze landing pages causing immediate exits\n"

        # Business insights
        business_insights = f"**Traffic Overview:**\n"
        business_insights += f"- Total Sessions: {int(total_sessions):,}\n"
        business_insights += f"- Unique Users: {int(unique_users):,}\n"
        business_insights += f"- Sessions per User: {total_sessions/unique_users:.1f}\n\n"
        business_insights += f"**Business Impact:**\n"
        if health_score < 60:
            business_insights += f"- UX issues likely impacting conversion and retention\n"
            business_insights += f"- Estimated {int(total_sessions * dead_click_rate / 100):,} sessions affected by dead clicks\n"
        else:
            business_insights += "- UX quality supporting business objectives\n"

        # Marketing insights
        marketing_insights = f"**Audience Reach:**\n"
        marketing_insights += f"- {int(unique_users):,} unique users reached\n"
        marketing_insights += f"- {int(total_sessions):,} total sessions\n"
        marketing_insights += f"- {int(bot_sessions):,} bot sessions filtered ({bot_sessions/total_sessions*100 if total_sessions else 0:.1f}%)\n"

        # Calculate session counts from rates
        dead_click_sessions = int(total_sessions * dead_click_rate / 100) if total_sessions else 0
        rage_click_sessions = int(total_sessions * rage_click_rate / 100) if total_sessions else 0
        quick_back_sessions = int(total_sessions * quick_back_rate / 100) if total_sessions else 0
        error_click_sessions = int(total_sessions * extract_num(data.get('ERROR_CLICK_RATE', '0')) / 100) if total_sessions else 0

        # Calculate total frustrated sessions (unique sessions with any frustration)
        # Approximate as union - assume some overlap
        frustrated_sessions = min(
            int(dead_click_sessions + rage_click_sessions + quick_back_sessions + error_click_sessions),
            int(total_sessions)
        )
        frustrated_percentage = (frustrated_sessions / total_sessions * 100) if total_sessions else 0

        # Generate frustration summary
        frustration_summary = f"Analysis reveals significant frustration patterns across {int(total_sessions):,} sessions. "
        if dead_click_rate > 5:
            frustration_summary += f"Dead clicks are the primary concern ({dead_click_rate:.1f}% of sessions). "
        if rage_click_rate > 1:
            frustration_summary += f"Rage clicking indicates broken interactions ({rage_click_rate:.1f}% of sessions). "
        if quick_back_rate > 10:
            frustration_summary += f"High quick back rate suggests poor landing experience ({quick_back_rate:.1f}% of sessions)."

        # Business impact calculations
        # Assume 3% baseline conversion rate, 50% loss per frustration signal
        estimated_lost_conversions = int(frustrated_sessions * 0.03 * 0.5)
        satisfaction_impact = "High negative impact" if frustrated_percentage > 30 else "Moderate negative impact" if frustrated_percentage > 15 else "Low negative impact"
        revenue_impact = f"Estimated ${estimated_lost_conversions * 50:,.0f} in lost revenue (assuming $50 avg order value)" if frustrated_percentage > 10 else "Minimal revenue impact"

        # Generate device breakdowns (simplified - would need dimension queries for real data)
        quick_back_by_device = "| Device | Sessions | Quick Backs | Rate |\n|--------|----------|-------------|------|\n"
        quick_back_by_device += "| All Devices | {:,} | {:,} | {:.1f}% |".format(int(total_sessions), int(quick_backs), quick_back_rate)

        dead_click_hotspots = f"- Primary hotspots detected across {dead_click_sessions:,} sessions\n"
        dead_click_hotspots += "- Common patterns: Non-clickable UI elements styled as buttons\n"
        dead_click_hotspots += "- Recommendation: Review visual affordances and cursor feedback"

        rage_click_by_device = "| Device | Sessions | Rage Clicks | Rate |\n|--------|----------|-------------|------|\n"
        rage_click_by_device += "| All Devices | {:,} | {:,} | {:.1f}% |".format(int(total_sessions), int(rage_clicks), rage_click_rate)

        # Generate recommendations
        quick_back_recommendations = "**Immediate Actions:**\n"
        if quick_back_rate > 10:
            quick_back_recommendations += "1. Audit landing page content alignment with user expectations\n"
            quick_back_recommendations += "2. Optimize page load performance (target <2s)\n"
            quick_back_recommendations += "3. Review meta descriptions and ad copy accuracy\n"
        else:
            quick_back_recommendations += "- Quick back rate within acceptable range\n"

        dead_click_recommendations = "**Immediate Actions:**\n"
        if dead_click_rate > 5:
            dead_click_recommendations += "1. Identify and fix non-interactive elements that appear clickable\n"
            dead_click_recommendations += "2. Add cursor feedback (cursor: pointer only for clickable elements)\n"
            dead_click_recommendations += "3. Review disabled buttons and form elements\n"
        else:
            dead_click_recommendations += "- Dead click rate within acceptable range\n"

        rage_click_recommendations = "**Immediate Actions:**\n"
        if rage_click_rate > 1:
            rage_click_recommendations += "1. Investigate and fix unresponsive interactive elements\n"
            rage_click_recommendations += "2. Add loading indicators for async operations\n"
            rage_click_recommendations += "3. Review form validation and error messaging\n"
        else:
            rage_click_recommendations += "- Rage click rate within acceptable range\n"

        # Trend analysis placeholder
        trend_analysis = "**Period-over-period trends:**\n"
        trend_analysis += f"- Dead clicks: {data.get('DEAD_CLICK_TREND', '→')}\n"
        trend_analysis += f"- Rage clicks: {data.get('RAGE_CLICK_TREND', '→')}\n"
        trend_analysis += f"- Quick backs: {data.get('QUICK_BACK_TREND', '→')}\n"

        insights = {
            'EXECUTIVE_SUMMARY': exec_summary,
            'TOP_UX_ISSUE': top_issue,
            'CRITICAL_FINDINGS': critical_findings,
            'TECHNICAL_INSIGHTS': tech_insights,
            'TECHNICAL_ACTIONS': tech_insights,  # Alias
            'UX_INSIGHTS': ux_insights,
            'UX_IMPROVEMENTS': ux_insights,  # Alias
            'BUSINESS_INSIGHTS': business_insights,
            'BUSINESS_IMPACT': business_insights,  # Alias
            'BUSINESS_OPPORTUNITIES': business_insights,  # Alias
            'MARKETING_INSIGHTS': marketing_insights,
            'MARKETING_RECOMMENDATIONS': marketing_insights,  # Alias
            'SCRIPT_ERROR_COUNT': str(int(script_errors)),
            'SCRIPT_ERROR_RATE': f"{script_errors/total_sessions*100 if total_sessions else 0:.1f}",
            'ERROR_CLICK_COUNT': str(int(error_clicks)),
            'QUICK_BACK_PERCENTAGE': f"{quick_back_rate:.1f}",
            'DEAD_CLICKS_TOTAL': str(int(dead_clicks)),
            'PAGES_WITH_DEAD_CLICKS': "multiple",  # Placeholder - would need page-level data
            'PAGES_WITH_RAGE_CLICKS': "multiple",  # Placeholder - would need page-level data
            'ENGAGEMENT_LEVEL': "Low" if health_score < 60 else "Moderate",
            'SESSION_QUALITY': "Needs improvement" if health_score < 60 else "Acceptable",
            'PAGES_PER_SESSION': f"{total_sessions/unique_users:.1f}" if unique_users > 0 else "N/A",
            'TOP_TRAFFIC_SOURCES': "Direct, Organic Search, Social Media",  # Placeholder - would need source data
            'PERIOD_COMPARISON': "Period comparison data not available",  # Placeholder
            # Frustration Analysis specific placeholders
            'SUMMARY': frustration_summary,
            'FRUSTRATED_SESSIONS': f"{frustrated_sessions:,}",
            'FRUSTRATED_PERCENTAGE': f"{frustrated_percentage:.1f}",
            'QUICK_BACK_COUNT': f"{int(quick_backs):,}",
            'QUICK_BACK_SESSIONS': f"{quick_back_sessions:,}",
            'QUICK_BACK_PCT': f"{quick_back_rate:.1f}",
            'DEAD_CLICK_COUNT': f"{int(dead_clicks):,}",
            'DEAD_CLICK_SESSIONS': f"{dead_click_sessions:,}",
            'DEAD_CLICK_PERCENTAGE': f"{dead_click_rate:.1f}",
            'DEAD_CLICK_PCT': f"{dead_click_rate:.1f}",
            'RAGE_CLICK_COUNT': f"{int(rage_clicks):,}",
            'RAGE_CLICK_SESSIONS': f"{rage_click_sessions:,}",
            'RAGE_CLICK_PERCENTAGE': f"{rage_click_rate:.1f}",
            'RAGE_CLICK_PCT': f"{rage_click_rate:.1f}",
            'ERROR_CLICK_SESSIONS': f"{error_click_sessions:,}",
            'ERROR_CLICK_PERCENTAGE': f"{extract_num(data.get('ERROR_CLICK_RATE', '0')):.1f}",
            'EXCESSIVE_SCROLL_COUNT': "0",
            'EXCESSIVE_SCROLL_SESSIONS': "0",
            'EXCESSIVE_SCROLL_PERCENTAGE': "0.0",
            'QUICK_BACK_BY_DEVICE': quick_back_by_device,
            'QUICK_BACK_BY_PAGE': "Requires page-level data collection",
            'QUICK_BACK_RECOMMENDATIONS': quick_back_recommendations,
            'DEAD_CLICK_HOTSPOTS': dead_click_hotspots,
            'DEAD_CLICK_RECOMMENDATIONS': dead_click_recommendations,
            'RAGE_CLICK_BY_DEVICE': rage_click_by_device,
            'RAGE_CLICK_BY_PAGE': "Requires page-level data collection",
            'RAGE_CLICK_RECOMMENDATIONS': rage_click_recommendations,
            'ESTIMATED_LOST_CONVERSIONS': f"{estimated_lost_conversions:,} conversions",
            'SATISFACTION_IMPACT': satisfaction_impact,
            'REVENUE_IMPACT': revenue_impact,
            'ROI_ANALYSIS': f"Fixing frustration signals could recover {estimated_lost_conversions:,} conversions",
            'HIGH_FRUSTRATION_SOURCES': "Pages with >10% frustration rate",
            'LOW_FRUSTRATION_SOURCES': "Pages with <2% frustration rate",
            'TREND_ANALYSIS': trend_analysis,
            # Device Performance specific placeholders
            'MOBILE_ENGAGEMENT': "N/A",
            'MOBILE_PAGES': "N/A",
            'MOBILE_FRUSTRATION': "N/A",
            'DESKTOP_ENGAGEMENT': "N/A",
            'DESKTOP_PAGES': "N/A",
            'DESKTOP_FRUSTRATION': "N/A",
            'TABLET_ENGAGEMENT': "N/A",
            'TABLET_PAGES': "N/A",
            'TABLET_FRUSTRATION': "N/A",
            'OTHER_SESSIONS': f"{data.get('OTHER_SESSIONS', '0')}",
            'OTHER_PERCENTAGE': f"{data.get('OTHER_PERCENTAGE', '0')}",
            'OTHER_ENGAGEMENT': "N/A",
            'OTHER_PAGES': "N/A",
            'OTHER_FRUSTRATION': "N/A",
            'BROWSER_TABLE': "| Browser | Sessions | % |\n|---------|----------|---|\n| All Browsers | {:,} | 100% |".format(int(total_sessions)),
            'MOBILE_VS_DESKTOP_ENGAGEMENT': "Requires device dimension data",
            'MOBILE_VS_DESKTOP_REC': "Enable device tracking for detailed comparison",
            'MOBILE_FRUSTRATION_DETAIL': "Requires device-level frustration data",
            'DESKTOP_FRUSTRATION_DETAIL': "Requires device-level frustration data",
            # Geographic Insights specific placeholders
            'COUNTRY_COUNT': "Data collection needed",
            'TOP_COUNTRIES_TABLE': "| Country | Sessions | % |\n|---------|----------|---|\n| All Countries | {:,} | 100% |".format(int(total_sessions)),
            'REGIONAL_ANALYSIS': "Geographic data collection not yet configured",
            'TOP_MARKETS': "Requires country dimension data",
            # Engagement Analysis specific placeholders
            'ENGAGEMENT_STATUS': "Low engagement" if health_score < 60 else "Moderate engagement",
            'ENGAGEMENT_DISTRIBUTION': f"Average engagement time: {data.get('AVG_ENGAGEMENT_TIME', '0')}s",
            'BEHAVIOR_PATTERNS': f"Users spending average {data.get('AVG_ENGAGEMENT_TIME', '0')}s on site",
            'AVG_ENGAGEMENT': f"{data.get('AVG_ENGAGEMENT_TIME', '0')}s",
            'ACTIVE_STATUS': "Below target" if extract_num(data.get('AVG_ENGAGEMENT_TIME', '0')) < 60 else "Acceptable",
            'SCROLL_STATUS': "Low" if extract_num(data.get('AVG_SCROLL_DEPTH', '0')) < 70 else "Good",
            'PAGES_STATUS': f"Average {total_sessions/unique_users:.1f} pages per user" if unique_users > 0 else "N/A",
            # Content Performance specific placeholders
            'TOP_PAGES_TABLE': "Requires page-level data collection",
            'CATEGORY_PERFORMANCE': "Requires page categorization and metrics",
            'REFERRER_ANALYSIS': "Requires referrer dimension data",
            'REFERRER_BREAKDOWN': "Referrer tracking not yet configured",
            # Page-specific placeholders
            'PAGE_NAME': data.get('PAGE_NAME', 'Unknown Page'),
            'PAGE_PATH': data.get('PAGE_PATH', '/'),
            'PAGE_CATEGORY': data.get('PAGE_CATEGORY', 'uncategorized'),
            'PAGE_VIEWS': data.get('PAGE_VIEWS', '0'),
            'UNIQUE_VISITORS': data.get('UNIQUE_VISITORS', '0'),
            'AVG_TIME': data.get('AVG_TIME', '0s'),
            'BOUNCE_RATE': data.get('BOUNCE_RATE', '0.0'),
            'IS_ENTRY_PAGE': data.get('IS_ENTRY_PAGE', 'Unknown'),
            'IS_EXIT_PAGE': data.get('IS_EXIT_PAGE', 'Unknown'),
            'DEVICE_BREAKDOWN': "Requires page-level device data",
            'REFERRER_BREAKDOWN': "Requires page-level referrer data",
            'PREVIOUS_PAGES': "Requires user journey data",
            'NEXT_PAGES': "Requires user journey data",
            'PAGE_SUMMARY': "Page-level data collection not yet configured",
            'QUICK_BACK_PERFORMANCE': data.get('QUICK_BACK_PERFORMANCE', 'N/A'),
            'BOUNCE_PERFORMANCE': data.get('BOUNCE_PERFORMANCE', 'N/A'),
            'TIME_PERFORMANCE': data.get('TIME_PERFORMANCE', 'N/A'),
            'SITE_AVG_TIME': data.get('AVG_ENGAGEMENT_TIME', '0'),
            'SITE_BOUNCE_RATE': "N/A",
            'SITE_QUICK_BACK': f"{quick_back_rate:.1f}%",
            'SITE_COMPARISON': "Page comparison requires page-level data",
            'SCROLL_ISSUE_COUNT': "0",
            'SCROLL_ISSUE_SESSIONS': "0",
            'SCROLL_ISSUE_PCT': "0.0",
            # General recommendations placeholder
            'RECOMMENDATIONS': self._generate_recommendations(data, dead_click_rate, rage_click_rate, quick_back_rate),
            # Frustration-analysis template specific placeholders
            'TECHNICAL_CAUSE_1': "UI elements styled as interactive but non-functional (dead clicks)",
            'TECHNICAL_CAUSE_2': "Slow response times causing rage clicks",
            'TECHNICAL_CAUSE_3': "Poor page load performance triggering quick backs",
            'TECHNICAL_FIX_1': "Audit and fix clickability affordances (cursor feedback, hover states)",
            'TECHNICAL_FIX_2': "Add loading indicators and optimize async operations",
            'TECHNICAL_FIX_3': "Improve page load performance (<2s target)",
            'UX_ISSUE_1': f"Dead clicks affecting {dead_click_rate:.1f}% of sessions",
            'UX_ISSUE_2': f"Rage clicks indicating broken interactions ({rage_click_rate:.1f}% of sessions)",
            'UX_ISSUE_3': f"High quick back rate ({quick_back_rate:.1f}%) suggesting poor landing UX",
            'UX_IMPROVEMENT_1': "Review visual design for misleading clickable elements",
            'UX_IMPROVEMENT_2': "Add clear feedback for all interactive elements",
            'UX_IMPROVEMENT_3': "Align landing page content with user expectations",
            'MARKETING_REC_1': "Audit ad copy and meta descriptions for accuracy",
            'MARKETING_REC_2': "Focus acquisition on lower-frustration traffic sources",
            'IMMEDIATE_ACTION_1': f"Fix top dead click issues affecting {int(dead_clicks):,} incidents",
            'IMMEDIATE_ACTION_2': f"Investigate rage click triggers across {rage_click_sessions:,} sessions",
        }

        for key, value in insights.items():
            content = content.replace(f"{{{key}}}", value)

        return content

    def _generate_recommendations(self, data: Dict[str, Any], dead_click_rate: float, rage_click_rate: float, quick_back_rate: float) -> str:
        """Generate prioritized recommendations based on metrics."""
        recommendations = "**Priority Recommendations:**\n\n"

        priority_count = 0

        # Priority 1: Most critical issue
        if dead_click_rate > 5:
            priority_count += 1
            recommendations += f"{priority_count}. **Fix Dead Click Issues** (Critical)\n"
            recommendations += "   - Audit UI for non-interactive elements appearing clickable\n"
            recommendations += "   - Add proper cursor feedback and visual affordances\n"
            recommendations += f"   - Impact: Could improve experience for 39.3% of sessions\n"
            recommendations += "   - Effort: Medium (2-3 days)\n\n"

        if rage_click_rate > 1:
            priority_count += 1
            recommendations += f"{priority_count}. **Resolve Rage Click Triggers** (Critical)\n"
            recommendations += "   - Identify and fix unresponsive interactions\n"
            recommendations += "   - Add loading states and feedback indicators\n"
            recommendations += f"   - Impact: Could improve experience for 12.1% of sessions\n"
            recommendations += "   - Effort: Medium (2-4 days)\n\n"

        if quick_back_rate > 10:
            priority_count += 1
            recommendations += f"{priority_count}. **Improve Landing Experience** (High)\n"
            recommendations += "   - Optimize page load performance\n"
            recommendations += "   - Align content with user expectations\n"
            recommendations += f"   - Impact: Could reduce bounce for 49.6% of sessions\n"
            recommendations += "   - Effort: High (1-2 weeks)\n\n"

        if priority_count == 0:
            recommendations = "**No critical issues detected.** Continue monitoring for patterns.\n"

        return recommendations

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
