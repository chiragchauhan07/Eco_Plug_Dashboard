import { useState } from 'react';
import { useAnalytics } from '../hooks/useAnalytics';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

const TIME_FILTER_OPTIONS = [
  { value: 'today', label: 'Today' },
  { value: '7days', label: 'Last 7 Days' },
  { value: '30days', label: 'Last 30 Days' },
  { value: '90days', label: 'Last 90 Days' },
  { value: 'year', label: 'Last Year' },
  { value: 'custom', label: 'Custom Range' },
];

const COLORS = ['#22c55e', '#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#6366f1'];

export function AnalyticsPage() {
  const [timeFilter, setTimeFilter] = useState<string>('30days');
  const [customStart, setCustomStart] = useState<string>('');
  const [customEnd, setCustomEnd] = useState<string>('');

  const {
    overview,
    trends,
    categories,
    sentiment,
    topIssues,
    locations,
    aiInsights,
    refetchAll,
  } = useAnalytics(
    timeFilter,
    timeFilter === 'custom' ? customStart : undefined,
    timeFilter === 'custom' ? customEnd : undefined
  );

  // Recharts mapping for Trends
  const trendData = (() => {
    const tData = trends.data;
    if (!tData || !tData.labels) return [];
    return tData.labels.map((lbl, idx) => ({
      name: lbl,
      feedback: tData.datasets[0]?.data[idx] ?? 0,
      complaints: tData.datasets[1]?.data[idx] ?? 0,
      rating: tData.datasets[2]?.data[idx] ?? 0,
      resolution: tData.datasets[3]?.data[idx] ?? 0,
    }));
  })();

  // Recharts mapping for Categories
  const categoryChartData = (() => {
    if (!categories.data || !categories.data.categories) return [];
    return categories.data.categories.map((c) => ({
      name: c.category,
      value: c.count,
      percentage: c.percentage,
    }));
  })();

  const sentimentChartData = (() => {
    if (!sentiment.data || !sentiment.data.distribution) return [];
    return sentiment.data.distribution.map((s) => ({
      name: s.sentiment,
      value: s.count,
      percentage: s.percentage,
    }));
  })();

  return (
    <main className="flex-1 p-lg md:p-xl overflow-y-auto max-w-7xl mx-auto w-full">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-xl gap-4">
        <div>
          <h2 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface">Analytics Overview</h2>
          <p className="font-body-md text-body-md text-secondary mt-1">Deep dive into network performance and user metrics.</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto items-stretch sm:items-center">
          {timeFilter === 'custom' && (
            <div className="flex items-center gap-2 bg-surface-container border border-outline-variant p-1.5 rounded-lg">
              <input
                type="date"
                value={customStart}
                onChange={(e) => setCustomStart(e.target.value)}
                className="bg-transparent border-none text-on-surface font-body-sm text-sm focus:outline-none py-0 w-28 cursor-pointer"
              />
              <span className="text-secondary font-body-sm text-sm">to</span>
              <input
                type="date"
                value={customEnd}
                onChange={(e) => setCustomEnd(e.target.value)}
                className="bg-transparent border-none text-on-surface font-body-sm text-sm focus:outline-none py-0 w-28 cursor-pointer"
              />
            </div>
          )}
          
          <div className="flex items-center bg-surface-container border border-outline-variant rounded-lg p-1">
            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              className="bg-transparent border-none font-label-md text-label-md text-on-surface focus:outline-none cursor-pointer pr-8 py-1.5"
            >
              {TIME_FILTER_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value} className="bg-surface">
                  {opt.label}
                </option>
              ))}
            </select>
            <button
              onClick={refetchAll}
              className="p-1 text-secondary hover:text-primary transition-colors ml-1"
              title="Refresh Analytics"
            >
              <span className="material-symbols-outlined text-md">refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Overview Grid */}
      <section className="mb-xl grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-md">
        {/* Total Feedback */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col justify-between min-h-[120px]">
          {overview.isLoading ? (
            <div className="animate-pulse flex flex-col justify-between h-full">
              <div className="h-4 bg-outline-variant rounded w-1/2"></div>
              <div className="h-8 bg-outline-variant rounded w-1/3 mt-2"></div>
            </div>
          ) : overview.error ? (
            <div className="flex flex-col items-start justify-between h-full">
              <span className="font-label-sm text-error">Failed to load</span>
              <button onClick={overview.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
            </div>
          ) : (
            <div>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Total Feedback</p>
              <h3 className="font-headline-md text-headline-md text-on-surface mt-2">{overview.data?.total_feedback ?? 0}</h3>
            </div>
          )}
        </div>

        {/* Total Complaints */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col justify-between min-h-[120px]">
          {overview.isLoading ? (
            <div className="animate-pulse flex flex-col justify-between h-full">
              <div className="h-4 bg-outline-variant rounded w-1/2"></div>
              <div className="h-8 bg-outline-variant rounded w-1/3 mt-2"></div>
            </div>
          ) : overview.error ? (
            <div className="flex flex-col items-start justify-between h-full">
              <span className="font-label-sm text-error">Failed to load</span>
              <button onClick={overview.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
            </div>
          ) : (
            <div>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Total Complaints</p>
              <h3 className="font-headline-md text-headline-md text-on-surface mt-2">{overview.data?.total_complaints ?? 0}</h3>
            </div>
          )}
        </div>

        {/* Average Rating */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col justify-between min-h-[120px]">
          {overview.isLoading ? (
            <div className="animate-pulse flex flex-col justify-between h-full">
              <div className="h-4 bg-outline-variant rounded w-1/2"></div>
              <div className="h-8 bg-outline-variant rounded w-1/3 mt-2"></div>
            </div>
          ) : overview.error ? (
            <div className="flex flex-col items-start justify-between h-full">
              <span className="font-label-sm text-error">Failed to load</span>
              <button onClick={overview.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
            </div>
          ) : (
            <div>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Average Rating</p>
              <h3 className="font-headline-md text-headline-md text-on-surface mt-2 flex items-center gap-1">
                {overview.data?.average_rating?.toFixed(1) ?? '0.0'}
                <span className="material-symbols-outlined text-primary text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
              </h3>
            </div>
          )}
        </div>

        {/* Complaint Rate */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col justify-between min-h-[120px]">
          {overview.isLoading ? (
            <div className="animate-pulse flex flex-col justify-between h-full">
              <div className="h-4 bg-outline-variant rounded w-1/2"></div>
              <div className="h-8 bg-outline-variant rounded w-1/3 mt-2"></div>
            </div>
          ) : overview.error ? (
            <div className="flex flex-col items-start justify-between h-full">
              <span className="font-label-sm text-error">Failed to load</span>
              <button onClick={overview.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
            </div>
          ) : (
            <div>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Complaint Rate</p>
              <h3 className="font-headline-md text-headline-md text-on-surface mt-2">{overview.data?.complaint_rate ?? 0}%</h3>
            </div>
          )}
        </div>

        {/* Resolution Rate */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col justify-between min-h-[120px]">
          {overview.isLoading ? (
            <div className="animate-pulse flex flex-col justify-between h-full">
              <div className="h-4 bg-outline-variant rounded w-1/2"></div>
              <div className="h-8 bg-outline-variant rounded w-1/3 mt-2"></div>
            </div>
          ) : overview.error ? (
            <div className="flex flex-col items-start justify-between h-full">
              <span className="font-label-sm text-error">Failed to load</span>
              <button onClick={overview.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
            </div>
          ) : (
            <div>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Resolution Rate</p>
              <h3 className="font-headline-md text-headline-md text-on-surface mt-2">{overview.data?.resolution_percentage ?? 0}%</h3>
            </div>
          )}
        </div>

        {/* Active Users */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col justify-between min-h-[120px]">
          {overview.isLoading ? (
            <div className="animate-pulse flex flex-col justify-between h-full">
              <div className="h-4 bg-outline-variant rounded w-1/2"></div>
              <div className="h-8 bg-outline-variant rounded w-1/3 mt-2"></div>
            </div>
          ) : overview.error ? (
            <div className="flex flex-col items-start justify-between h-full">
              <span className="font-label-sm text-error">Failed to load</span>
              <button onClick={overview.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
            </div>
          ) : (
            <div>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Active Users</p>
              <h3 className="font-headline-md text-headline-md text-on-surface mt-2">{overview.data?.active_users ?? 0}</h3>
            </div>
          )}
        </div>

        {/* Energy Delivered */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col justify-between min-h-[120px]">
          {overview.isLoading ? (
            <div className="animate-pulse flex flex-col justify-between h-full">
              <div className="h-4 bg-outline-variant rounded w-1/2"></div>
              <div className="h-8 bg-outline-variant rounded w-1/3 mt-2"></div>
            </div>
          ) : overview.error ? (
            <div className="flex flex-col items-start justify-between h-full">
              <span className="font-label-sm text-error">Failed to load</span>
              <button onClick={overview.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
            </div>
          ) : (
            <div>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Energy Delivered</p>
              <h3 className="font-headline-md text-headline-md text-on-surface mt-2">{overview.data?.energy_delivered?.toFixed(1) ?? '0.0'} kWh</h3>
            </div>
          )}
        </div>

        {/* Energy Saved */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col justify-between min-h-[120px]">
          {overview.isLoading ? (
            <div className="animate-pulse flex flex-col justify-between h-full">
              <div className="h-4 bg-outline-variant rounded w-1/2"></div>
              <div className="h-8 bg-outline-variant rounded w-1/3 mt-2"></div>
            </div>
          ) : overview.error ? (
            <div className="flex flex-col items-start justify-between h-full">
              <span className="font-label-sm text-error">Failed to load</span>
              <button onClick={overview.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
            </div>
          ) : (
            <div>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Energy Saved</p>
              <h3 className="font-headline-md text-headline-md text-on-surface mt-2">{overview.data?.energy_saved?.toFixed(1) ?? '0.0'} kWh</h3>
            </div>
          )}
        </div>
      </section>

      {/* AI Insights Section */}
      <section className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm mb-xl">
        <div className="flex justify-between items-center mb-md pb-3 border-b border-outline-variant">
          <h3 className="font-headline-md text-headline-md text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">auto_awesome</span>
            AI Analytics Insights
          </h3>
          <span className="font-label-sm bg-secondary-container text-on-secondary-container px-2 py-1 rounded">Powered by Gemini AI</span>
        </div>

        {aiInsights.isLoading ? (
          <div className="flex space-x-2 justify-center items-center py-12" id="ai-insights-three-dot-loader">
            <div className="h-3 w-3 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div className="h-3 w-3 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div className="h-3 w-3 bg-primary rounded-full animate-bounce"></div>
          </div>
        ) : aiInsights.error ? (
          <div className="text-error bg-error-container p-md rounded-lg flex flex-col items-start">
            <p className="font-body-md mb-2">{aiInsights.error}</p>
            <button onClick={aiInsights.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
            {/* Positive Trends */}
            <div className="bg-surface-container rounded-lg p-md border border-outline-variant/60">
              <h4 className="font-headline-sm text-lg text-primary flex items-center gap-1.5 mb-3">
                <span className="material-symbols-outlined text-sm">trending_up</span> Positive Trends
              </h4>
              <ul className="space-y-2 list-disc pl-5 font-body-sm text-sm text-on-surface">
                {aiInsights.data?.trends?.map((t, idx) => <li key={idx}>{t}</li>) ?? <li>No positive trends generated.</li>}
              </ul>
            </div>

            {/* Risk Indicators */}
            <div className="bg-surface-container rounded-lg p-md border border-outline-variant/60">
              <h4 className="font-headline-sm text-lg text-error flex items-center gap-1.5 mb-3">
                <span className="material-symbols-outlined text-sm">warning</span> Risk Indicators
              </h4>
              <ul className="space-y-2 list-disc pl-5 font-body-sm text-sm text-on-surface">
                {aiInsights.data?.anomalies?.map((a, idx) => <li key={idx}>{a}</li>) ?? <li>No risk indicators generated.</li>}
              </ul>
            </div>

            {/* Opportunities */}
            <div className="bg-surface-container rounded-lg p-md border border-outline-variant/60">
              <h4 className="font-headline-sm text-lg text-blue-500 flex items-center gap-1.5 mb-3">
                <span className="material-symbols-outlined text-sm">lightbulb</span> Opportunities
              </h4>
              <ul className="space-y-2 list-disc pl-5 font-body-sm text-sm text-on-surface">
                {aiInsights.data?.recommendations?.map((r, idx) => <li key={idx}>{r}</li>) ?? <li>No opportunities generated.</li>}
              </ul>
            </div>
          </div>
        )}
      </section>

      {/* Trend Charts Section */}
      <section className="grid grid-cols-1 xl:grid-cols-2 gap-lg mb-xl">
        {/* Feedback & Complaint Trends */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm">
          <div className="flex justify-between items-center mb-md">
            <div>
              <h3 className="font-headline-md text-headline-md text-on-surface">Feedback & Complaint Trends</h3>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest mt-1">Volume patterns</p>
            </div>
          </div>
          {trends.isLoading ? (
            <div className="animate-pulse bg-surface-container rounded-lg h-[300px]"></div>
          ) : trends.error ? (
            <div className="flex flex-col items-center justify-center bg-surface-container rounded-lg h-[300px] gap-2 p-md">
              <span className="text-error font-body-md">{trends.error}</span>
              <button onClick={trends.refetch} className="px-3 py-1.5 bg-primary text-on-primary rounded font-label-md text-label-md">Retry</button>
            </div>
          ) : trendData.length === 0 ? (
            <div className="flex items-center justify-center bg-surface-container rounded-lg h-[300px]">
              <span className="font-body-sm text-secondary">No trend data available for this range.</span>
            </div>
          ) : (
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="name" stroke="#a1a1aa" fontSize={12} />
                  <YAxis stroke="#a1a1aa" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a' }} labelStyle={{ color: '#fff' }} />
                  <Legend />
                  <Bar dataKey="feedback" name="Feedback" fill="#22c55e" />
                  <Bar dataKey="complaints" name="Complaints" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Rating & Resolution Trends */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm">
          <div className="flex justify-between items-center mb-md">
            <div>
              <h3 className="font-headline-md text-headline-md text-on-surface">Rating & Resolution Trends</h3>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest mt-1">Performance over time</p>
            </div>
          </div>
          {trends.isLoading ? (
            <div className="animate-pulse bg-surface-container rounded-lg h-[300px]"></div>
          ) : trends.error ? (
            <div className="flex flex-col items-center justify-center bg-surface-container rounded-lg h-[300px] gap-2 p-md">
              <span className="text-error font-body-md">{trends.error}</span>
              <button onClick={trends.refetch} className="px-3 py-1.5 bg-primary text-on-primary rounded font-label-md text-label-md">Retry</button>
            </div>
          ) : trendData.length === 0 ? (
            <div className="flex items-center justify-center bg-surface-container rounded-lg h-[300px]">
              <span className="font-body-sm text-secondary">No trend data available for this range.</span>
            </div>
          ) : (
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="name" stroke="#a1a1aa" fontSize={12} />
                  <YAxis yAxisId="left" stroke="#22c55e" fontSize={12} domain={[0, 5]} />
                  <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" fontSize={12} domain={[0, 100]} />
                  <Tooltip contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a' }} labelStyle={{ color: '#fff' }} />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="rating" name="Avg Rating" stroke="#22c55e" activeDot={{ r: 8 }} />
                  <Line yAxisId="right" type="monotone" dataKey="resolution" name="Resolution %" stroke="#3b82f6" activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </section>

      {/* Category & Sentiment Distributions */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-lg mb-xl">
        {/* Category Distribution */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm">
          <h3 className="font-headline-md text-headline-md text-on-surface mb-md">Category Distribution</h3>
          {categories.isLoading ? (
            <div className="animate-pulse bg-surface-container rounded-lg h-[260px]"></div>
          ) : categories.error ? (
            <div className="flex flex-col items-center justify-center bg-surface-container rounded-lg h-[260px] gap-2 p-md">
              <span className="text-error font-body-md">{categories.error}</span>
              <button onClick={categories.refetch} className="px-3 py-1.5 bg-primary text-on-primary rounded font-label-md text-label-md">Retry</button>
            </div>
          ) : categoryChartData.length === 0 ? (
            <div className="flex items-center justify-center bg-surface-container rounded-lg h-[260px]">
              <span className="font-body-sm text-secondary">No categories found.</span>
            </div>
          ) : (
            <div className="h-[260px] flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {categoryChartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, name, props) => [`${value} (${props.payload.percentage}%)`, name]} />
                  <Legend layout="vertical" align="right" verticalAlign="middle" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Sentiment Distribution */}
        <div className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm">
          <h3 className="font-headline-md text-headline-md text-on-surface mb-md">Sentiment Distribution</h3>
          {sentiment.isLoading ? (
            <div className="animate-pulse bg-surface-container rounded-lg h-[260px]"></div>
          ) : sentiment.error ? (
            <div className="flex flex-col items-center justify-center bg-surface-container rounded-lg h-[260px] gap-2 p-md">
              <span className="text-error font-body-md">{sentiment.error}</span>
              <button onClick={sentiment.refetch} className="px-3 py-1.5 bg-primary text-on-primary rounded font-label-md text-label-md">Retry</button>
            </div>
          ) : sentimentChartData.length === 0 ? (
            /* Sentiment Empty State */
            <div className="flex flex-col items-center justify-center bg-surface-container/50 border border-dashed border-outline-variant rounded-lg h-[260px] p-lg text-center">
              <span className="material-symbols-outlined text-4xl text-secondary mb-2">sentiment_satisfied</span>
              <h4 className="font-headline-sm text-sm font-semibold text-on-surface mb-1">No Sentiment Data Available</h4>
              <p className="font-body-sm text-sm text-secondary max-w-xs">AI sentiment analysis has not been stored for the selected date range yet.</p>
            </div>
          ) : (
            <div className="h-[260px] flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {sentimentChartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, name, props) => [`${value} (${props.payload.percentage}%)`, name]} />
                  <Legend layout="vertical" align="right" verticalAlign="middle" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </section>

      {/* Top Issues Section */}
      <section className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm mb-xl">
        <h3 className="font-headline-md text-headline-md text-on-surface mb-md">Top Recurring Issues</h3>
        {topIssues.isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-10 bg-surface-container rounded"></div>
            <div className="h-10 bg-surface-container rounded"></div>
            <div className="h-10 bg-surface-container rounded"></div>
          </div>
        ) : topIssues.error ? (
          <div className="text-error bg-error-container p-md rounded-lg flex flex-col items-start">
            <p className="font-body-md mb-2">{topIssues.error}</p>
            <button onClick={topIssues.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
          </div>
        ) : topIssues.data?.issues.length === 0 ? (
          <div className="text-center py-6 text-secondary font-body-sm">No recurring issues identified.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-outline-variant bg-surface-container-low">
                  <th className="p-3 font-label-sm text-label-sm text-secondary font-medium">Issue Category</th>
                  <th className="p-3 font-label-sm text-label-sm text-secondary font-medium">Count</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant font-body-sm text-sm">
                {topIssues.data?.issues.map((i, idx) => (
                  <tr key={idx} className="hover:bg-surface-container transition-colors">
                    <td className="p-3 font-semibold text-on-surface">{i.issue}</td>
                    <td className="p-3 text-secondary">{i.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Location Insights Section */}
      <section className="bg-surface rounded-xl border border-outline-variant p-lg shadow-sm mb-xl">
        <h3 className="font-headline-md text-headline-md text-on-surface mb-md">Location Insights</h3>
        {locations.isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-md animate-pulse">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-28 bg-surface-container rounded-lg border border-outline-variant/60"></div>
            ))}
          </div>
        ) : locations.error ? (
          <div className="text-error bg-error-container p-md rounded-lg flex flex-col items-start">
            <p className="font-body-md mb-2">{locations.error}</p>
            <button onClick={locations.refetch} className="text-sm font-semibold hover:underline text-primary">Retry</button>
          </div>
        ) : !locations.data || (
          locations.data.most_complaints_by_location.length === 0 &&
          locations.data.highest_rated_locations.length === 0 &&
          locations.data.lowest_rated_locations.length === 0 &&
          locations.data.most_active_chargers.length === 0
        ) ? (
          /* Location Empty State */
          <div className="flex flex-col items-center justify-center bg-surface-container/50 border border-dashed border-outline-variant rounded-lg p-lg text-center">
            <span className="material-symbols-outlined text-4xl text-secondary mb-2">location_off</span>
            <h4 className="font-headline-sm text-sm font-semibold text-on-surface mb-1">No Location Data Available</h4>
            <p className="font-body-sm text-sm text-secondary">Charger location details are currently missing or unconfigured.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-md">
            {/* Highest Rated */}
            <div className="bg-surface-container border border-outline-variant/60 rounded-lg p-md">
              <span className="material-symbols-outlined text-primary text-2xl mb-1">star</span>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Highest Rated Location</p>
              <h4 className="font-body-md font-semibold text-on-surface mt-2">
                {locations.data.highest_rated_locations[0]?.location_name || 'N/A'}
              </h4>
              <p className="font-label-sm text-secondary mt-1">
                {locations.data.highest_rated_locations[0] 
                  ? `Rating: ${locations.data.highest_rated_locations[0].average_rating.toFixed(1)}/5` 
                  : 'No rating records'}
              </p>
            </div>

            {/* Lowest Rated */}
            <div className="bg-surface-container border border-outline-variant/60 rounded-lg p-md">
              <span className="material-symbols-outlined text-warning text-2xl mb-1">star_half</span>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Lowest Rated Location</p>
              <h4 className="font-body-md font-semibold text-on-surface mt-2">
                {locations.data.lowest_rated_locations[0]?.location_name || 'N/A'}
              </h4>
              <p className="font-label-sm text-secondary mt-1">
                {locations.data.lowest_rated_locations[0] 
                  ? `Rating: ${locations.data.lowest_rated_locations[0].average_rating.toFixed(1)}/5` 
                  : 'No rating records'}
              </p>
            </div>

            {/* Most Complaints */}
            <div className="bg-surface-container border border-outline-variant/60 rounded-lg p-md">
              <span className="material-symbols-outlined text-error text-2xl mb-1">report_problem</span>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Most Complaints Location</p>
              <h4 className="font-body-md font-semibold text-on-surface mt-2">
                {locations.data.most_complaints_by_location[0]?.location_name || 'N/A'}
              </h4>
              <p className="font-label-sm text-secondary mt-1">
                {locations.data.most_complaints_by_location[0] 
                  ? `${locations.data.most_complaints_by_location[0].complaint_count} complaints` 
                  : 'No complaints'}
              </p>
            </div>

            {/* Most Active Charger */}
            <div className="bg-surface-container border border-outline-variant/60 rounded-lg p-md">
              <span className="material-symbols-outlined text-blue-500 text-2xl mb-1">ev_station</span>
              <p className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">Most Active Charger</p>
              <h4 className="font-body-md font-semibold text-on-surface mt-2">
                {locations.data.most_active_chargers[0]?.location_name || 'N/A'}
              </h4>
              <p className="font-label-sm text-secondary mt-1">
                {locations.data.most_active_chargers[0] 
                  ? `${locations.data.most_active_chargers[0].session_count} sessions` 
                  : 'No sessions'}
              </p>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
