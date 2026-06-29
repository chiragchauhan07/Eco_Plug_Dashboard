import typing
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard import DashboardRepository
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    TrendResponse,
    TrendDataset,
    CategoryDistributionResponse,
    CategoryDistributionItem,
    SentimentDistributionResponse,
    SentimentDistributionItem,
    TopIssuesResponse,
    TopIssueItem,
    LocationInsightsResponse,
    LocationInsightItem,
    AIAnalyticsInsightsResponse,
)
from app.ai.providers.factory import ProviderFactory
from app.ai.prompts import templates
from app.ai.cache import ai_cache

class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = DashboardRepository(db)

    @staticmethod
    def resolve_time_filter(
        time_filter: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Tuple[datetime, datetime]:
        end = datetime.now(timezone.utc)
        if time_filter == "today":
            start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "7days":
            start = end - timedelta(days=7)
        elif time_filter == "30days":
            start = end - timedelta(days=30)
        elif time_filter == "90days":
            start = end - timedelta(days=90)
        elif time_filter == "year":
            start = end - timedelta(days=365)
        elif time_filter == "custom":
            if not start_date or not end_date:
                start = end - timedelta(days=30)
            else:
                start = start_date if start_date.tzinfo else start_date.replace(tzinfo=timezone.utc)
                end = end_date if end_date.tzinfo else end_date.replace(tzinfo=timezone.utc)
        else:
            start = end - timedelta(days=30)
        return start, end

    @staticmethod
    def _determine_interval(start: datetime, end: datetime) -> str:
        diff = end - start
        if diff.days <= 7:
            return "day"
        elif diff.days <= 90:
            return "week"
        else:
            return "month"

    async def get_overview_data(self, start: datetime, end: datetime) -> AnalyticsOverviewResponse:
        stats = await self.repo.get_period_stats(start, end)
        
        total_feedback = stats["feedback"]
        total_complaints = stats["complaints"]
        average_rating = stats["average_rating"]
        open_complaints = stats["open_complaints"]
        closed_complaints = stats["closed_complaints"]
        
        # Complaint rate relative to sessions
        total_sessions = stats["sessions"]
        complaint_rate = (total_complaints / total_sessions * 100.0) if total_sessions > 0 else 0.0
        
        resolved_complaints = closed_complaints
        pending_complaints = open_complaints
        
        resolution_percentage = (resolved_complaints / total_complaints * 100.0) if total_complaints > 0 else 100.0
        
        return AnalyticsOverviewResponse(
            total_feedback=total_feedback,
            total_complaints=total_complaints,
            average_rating=average_rating,
            complaint_rate=round(complaint_rate, 2),
            resolved_complaints=resolved_complaints,
            pending_complaints=pending_complaints,
            resolution_percentage=round(resolution_percentage, 2),
            average_response_time=None,
            active_users=stats["users"],
            total_sessions=total_sessions,
            energy_delivered=stats["energy"],
            energy_saved=round(stats["energy"] * 0.8, 2),  # Inferred heuristic
        )

    async def get_trends_data(self, start: datetime, end: datetime) -> TrendResponse:
        interval = self._determine_interval(start, end)
        
        fb_trend = await self.repo.get_feedback_trend_analytics(start, end, interval)
        cp_trend = await self.repo.get_complaints_trend_analytics(start, end, interval)
        rt_trend = await self.repo.get_rating_trend_analytics(start, end, interval)
        rs_trend = await self.repo.get_complaint_resolution_trend_analytics(start, end, interval)
        
        # Combine labels chronologically
        labels_set = set()
        trends_lists: list[list[tuple[str, typing.Any]]] = [fb_trend, cp_trend, rt_trend, rs_trend]
        for t in trends_lists:
            for lbl, _ in t:
                labels_set.add(lbl)
        labels = sorted(list(labels_set))
        
        # Map values to dataset
        fb_map = dict(fb_trend)
        cp_map = dict(cp_trend)
        rt_map = dict(rt_trend)
        rs_map = dict(rs_trend)
        
        fb_data = [float(fb_map.get(lbl, 0)) for lbl in labels]
        cp_data = [float(cp_map.get(lbl, 0)) for lbl in labels]
        rt_data = [float(rt_map.get(lbl, 0.0)) for lbl in labels]
        rs_data = [float(rs_map.get(lbl, 0.0)) for lbl in labels]
        
        return TrendResponse(
            labels=labels,
            datasets=[
                TrendDataset(label="Feedback Count", data=fb_data),
                TrendDataset(label="Complaint Count", data=cp_data),
                TrendDataset(label="Average Rating", data=rt_data),
                TrendDataset(label="Resolution Percentage", data=rs_data),
            ]
        )

    async def get_categories_data(self, start: datetime, end: datetime) -> CategoryDistributionResponse:
        categories = await self.repo.get_feedback_category_dist(start, end)
        total = sum(count for _, count in categories)
        
        items = []
        for cat, count in categories:
            pct = (count / total * 100.0) if total > 0 else 0.0
            items.append(
                CategoryDistributionItem(
                    category=cat,
                    count=count,
                    percentage=round(pct, 2)
                )
            )
        # Sort descending by count
        items.sort(key=lambda x: x.count, reverse=True)
        return CategoryDistributionResponse(categories=items)

    async def get_sentiment_data(self, start: datetime, end: datetime) -> SentimentDistributionResponse:
        sentiments = await self.repo.get_sentiment_distribution(start, end)
        total = sum(count for _, count in sentiments)
        
        items = []
        for sent, count in sentiments:
            pct = (count / total * 100.0) if total > 0 else 0.0
            items.append(
                SentimentDistributionItem(
                    sentiment=sent,
                    count=count,
                    percentage=round(pct, 2)
                )
            )
        return SentimentDistributionResponse(distribution=items)

    async def get_top_issues_data(self, start: datetime, end: datetime) -> TopIssuesResponse:
        issues = await self.repo.get_top_complaint_categories(start, end)
        items = [TopIssueItem(issue=issue, count=count) for issue, count in issues]
        return TopIssuesResponse(issues=items)

    async def get_location_insights_data(self) -> LocationInsightsResponse:
        # Re-use existing get_charger_analytics method which queries location info
        rows = await self.repo.get_charger_analytics()
        
        if not rows:
            return LocationInsightsResponse(
                most_complaints_by_location=[],
                highest_rated_locations=[],
                lowest_rated_locations=[],
                most_active_chargers=[]
            )
            
        items = [
            LocationInsightItem(
                location_name=r["charger_name"],
                complaint_count=r["complaint_count"],
                average_rating=r["average_rating"],
                session_count=r["session_count"]
            )
            for r in rows
        ]
        
        # 1. Most complaints by location (sorted by complaint_count desc)
        most_complaints = sorted(items, key=lambda x: x.complaint_count, reverse=True)
        
        # 2. Highest rated location (sorted by average_rating desc, filter rating > 0)
        highest_rated = sorted(
            [i for i in items if i.average_rating > 0],
            key=lambda x: x.average_rating,
            reverse=True
        )
        
        # 3. Lowest rated location (sorted by average_rating asc, filter rating > 0)
        lowest_rated = sorted(
            [i for i in items if i.average_rating > 0],
            key=lambda x: x.average_rating,
            reverse=False
        )
        
        # 4. Most active chargers (sorted by session_count desc)
        most_active = sorted(items, key=lambda x: x.session_count, reverse=True)
        
        return LocationInsightsResponse(
            most_complaints_by_location=most_complaints[:5],
            highest_rated_locations=highest_rated[:5],
            lowest_rated_locations=lowest_rated[:5],
            most_active_chargers=most_active[:5]
        )

    async def get_ai_insights_data(
        self, time_filter: str, start: datetime, end: datetime
    ) -> AIAnalyticsInsightsResponse:
        cache_key = f"analytics_ai_insights_{time_filter}_{start.timestamp()}_{end.timestamp()}"
        cached = await ai_cache.get(cache_key)
        if cached:
            return typing.cast(AIAnalyticsInsightsResponse, cached)
            
        # Single-pass database collections first
        overview = await self.get_overview_data(start, end)
        top_issues = await self.get_top_issues_data(start, end)
        sentiment = await self.get_sentiment_data(start, end)
        locations = await self.get_location_insights_data()
        categories = await self.get_categories_data(start, end)
        
        # Build prompt context
        category_distribution_str = ", ".join([f"{i.category}: {i.count} ({i.percentage}%)" for i in categories.categories]) or "None"
        top_categories_str = ", ".join([f"{i.issue} ({i.count})" for i in top_issues.issues]) or "None"
        sentiment_distribution_str = ", ".join([f"{i.sentiment}: {i.percentage}%" for i in sentiment.distribution]) or "None"
        
        location_summary = []
        if locations.most_complaints_by_location:
            location_summary.append(f"Top complaints at: {locations.most_complaints_by_location[0].location_name}")
        if locations.highest_rated_locations:
            location_summary.append(f"Highest rated location: {locations.highest_rated_locations[0].location_name}")
        location_insights_str = "; ".join(location_summary) or "No location records"
        
        prompt = templates.ANALYTICS_AI_INSIGHTS_PROMPT.format(
            total_feedback=overview.total_feedback,
            average_rating=overview.average_rating,
            category_distribution=category_distribution_str,
            total_complaints=overview.total_complaints,
            complaint_rate=overview.complaint_rate,
            resolved_complaints=overview.resolved_complaints,
            pending_complaints=overview.pending_complaints,
            resolution_percentage=overview.resolution_percentage,
            total_sessions=overview.total_sessions,
            energy_delivered=overview.energy_delivered,
            top_categories=top_categories_str,
            sentiment_distribution=sentiment_distribution_str,
            location_insights=location_insights_str
        )
        
        provider = ProviderFactory.get_provider()
        result = await provider.generate_structured(
            prompt=prompt,
            schema=AIAnalyticsInsightsResponse
        )
        
        result_typed = typing.cast(AIAnalyticsInsightsResponse, result)
        
        # Cache for 15 minutes
        await ai_cache.set(cache_key, result_typed, ttl=900)
        return result_typed
