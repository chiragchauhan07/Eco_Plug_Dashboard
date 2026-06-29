import { useDashboard } from '../hooks/useDashboard';
import { useAI } from '../hooks/useAI';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export function DashboardPage() {
  const {
    overview,
    feedbackAnalytics,
    complaintAnalytics,
    recentActivity,
    isLoading,
    error
  } = useDashboard();

  const {
    executiveSummary,
    isSummaryLoading,
    summaryError,
    refreshExecutiveSummary,
    analyticsInsights,
    isInsightsLoading,
    insightsError,
    refreshAnalyticsInsights,
  } = useAI();

  const formatTrend = (value?: number, invertColor: boolean = false) => {
    if (value === undefined || value === null) return (
      <p className="font-body-sm text-body-sm text-secondary mt-1 flex items-center"><span className="material-symbols-outlined text-sm">horizontal_rule</span> No change</p>
    );
    const isPositive = value >= 0;
    
    let colorClass = isPositive ? 'text-primary' : 'text-error';
    if (invertColor) {
        colorClass = isPositive ? 'text-error' : 'text-primary';
    }

    return (
      <p className={`font-body-sm text-body-sm mt-1 flex items-center ${colorClass}`}>
        <span className="material-symbols-outlined text-sm">
          {isPositive ? 'trending_up' : 'trending_down'}
        </span>
        {' '}{Math.abs(value)}% vs last month
      </p>
    );
  };

  const getActivityIconAndColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'complaint':
        return 'bg-error';
      case 'session':
        return 'bg-primary';
      case 'feedback':
      default:
        return 'bg-surface-variant';
    }
  };

  const feedbackData = feedbackAnalytics?.feedback_over_time?.labels?.map((label, idx) => ({
    name: label,
    value: feedbackAnalytics.feedback_over_time.datasets[0]?.data[idx] || 0
  })) || [];

  const complaintData = complaintAnalytics?.status_distribution?.labels?.map((label, idx) => ({
    name: label,
    value: complaintAnalytics.status_distribution.datasets[0]?.data[idx] || 0
  })) || [];

  const parseBullets = (text?: string) => {
    if (!text) return [];
    return text
      .split('\n')
      .map(line => line.replace(/^-\s*/, '').trim())
      .filter(line => line.length > 0);
  };

  return (
    <main className="flex-1 p-lg md:p-xl overflow-y-auto max-w-7xl mx-auto w-full">
      {/* Greeting */}
      <section className="mb-xl">
        <h2 className="font-headline-lg text-headline-lg md:font-display-lg md:text-display-lg text-on-surface mb-xs tracking-tight">Good Morning, Admin.</h2>
        <p className="font-body-lg text-body-lg text-secondary">Here's what needs your attention today.</p>
      </section>

      {/* AI Highlights */}
      <section className="mb-xl">
        <div className="bg-surface border border-outline-variant rounded-xl p-lg flex flex-col relative overflow-hidden min-h-[180px]">
          <div className="flex justify-between items-center mb-md">
            <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">auto_awesome</span>
              AI Highlights
            </h3>
            <button 
              onClick={refreshExecutiveSummary}
              disabled={isSummaryLoading}
              className="text-secondary hover:text-primary transition-colors disabled:opacity-50"
              title="Refresh Highlights"
            >
              <span className={`material-symbols-outlined ${isSummaryLoading ? 'animate-spin' : ''}`}>sync</span>
            </button>
          </div>
          
          {isSummaryLoading ? (
            <div className="flex space-x-2 justify-center items-center py-8 h-[120px]" id="highlights-three-dot-loader">
              <div className="h-2.5 w-2.5 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="h-2.5 w-2.5 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="h-2.5 w-2.5 bg-primary rounded-full animate-bounce"></div>
            </div>
          ) : summaryError ? (
            <div className="text-error bg-error-container p-md rounded-lg flex flex-col items-start">
              <p className="font-body-md mb-2">{summaryError}</p>
              <button onClick={refreshExecutiveSummary} className="text-sm font-semibold hover:underline">Retry</button>
            </div>
          ) : (
            <>
              <ul className="space-y-3 font-body-lg text-on-surface mb-4 leading-relaxed list-disc pl-5">
                {parseBullets(executiveSummary?.summary).map((bullet, i) => (
                  <li key={i} className="text-on-surface">{bullet}</li>
                ))}
              </ul>
              
              <div className="mt-md pt-md border-t border-outline-variant flex justify-between items-center">
                <span className="font-label-sm text-tertiary">Generated {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                <span className="font-label-sm bg-secondary-container text-on-secondary-container px-2 py-1 rounded">Powered by Gemini AI</span>
              </div>
            </>
          )}
        </div>
      </section>

      {/* Priority Alerts */}
      <section className="mb-xl grid grid-cols-1 md:grid-cols-3 gap-md">
        {isLoading ? (
          <div className="bg-error-container/20 p-lg rounded-xl border border-error/10 animate-pulse h-[140px] flex flex-col justify-between">
            <div className="h-6 bg-error/10 rounded w-1/4"></div>
            <div className="h-8 bg-error/10 rounded w-1/2"></div>
          </div>
        ) : (
          <div className="bg-error-container text-on-error-container p-lg rounded-xl flex flex-col justify-between border border-error/20 relative overflow-hidden group hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex justify-between items-start mb-4 relative z-10">
              <span className="material-symbols-outlined text-3xl">report</span>
              <span className="bg-error text-on-error px-2 py-1 rounded-full font-label-sm text-label-sm font-bold">CRITICAL</span>
            </div>
            <div className="relative z-10">
              <h3 className="font-headline-md text-headline-md mb-1">{overview?.open_complaints || 0}</h3>
              <p className="font-label-md text-label-md opacity-90">Open Complaints</p>
            </div>
            <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform duration-500">
              <span className="material-symbols-outlined text-9xl">report</span>
            </div>
          </div>
        )}
        
        {isLoading ? (
          <div className="bg-surface-container-high p-lg rounded-xl border border-outline-variant animate-pulse h-[140px] flex flex-col justify-between">
            <div className="h-6 bg-surface-variant rounded w-1/4"></div>
            <div className="h-8 bg-surface-variant rounded w-1/2"></div>
          </div>
        ) : (
          <div className="bg-surface-container-high p-lg rounded-xl flex flex-col justify-between border border-outline-variant relative overflow-hidden group hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex justify-between items-start mb-4 relative z-10">
              <span className="material-symbols-outlined text-3xl text-secondary">ev_station</span>
              <span className="bg-surface-variant text-on-surface-variant px-2 py-1 rounded-full font-label-sm text-label-sm font-bold">WARNING</span>
            </div>
            <div className="relative z-10">
              <h3 className="font-headline-md text-headline-md mb-1 text-on-surface">{overview?.closed_complaints || 0}</h3>
              <p className="font-label-md text-label-md text-secondary">Closed Complaints</p>
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="bg-secondary-container/20 p-lg rounded-xl border border-secondary/10 animate-pulse h-[140px] flex flex-col justify-between">
            <div className="h-6 bg-secondary/10 rounded w-1/4"></div>
            <div className="h-8 bg-secondary/10 rounded w-1/2"></div>
          </div>
        ) : (
          <div className="bg-secondary-container text-on-secondary-container p-lg rounded-xl flex flex-col justify-between border border-secondary/20 relative overflow-hidden group hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex justify-between items-start mb-4 relative z-10">
              <span className="material-symbols-outlined text-3xl">thumb_down</span>
              <span className="bg-secondary text-on-secondary px-2 py-1 rounded-full font-label-sm text-label-sm font-bold">TODAY</span>
            </div>
            <div className="relative z-10">
              <h3 className="font-headline-md text-headline-md mb-1">{overview?.total_feedback || 0}</h3>
              <p className="font-label-md text-label-md opacity-90">Total Feedback</p>
            </div>
          </div>
        )}
      </section>

      {/* Layout Grid: Main Content & Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-xl">
        {/* Main Column (Charts & Metrics) */}
        <div className="lg:col-span-3 space-y-xl">
          {/* Key Metrics Bento */}
          <section>
            <h3 className="font-label-md text-label-md text-secondary uppercase tracking-widest mb-md">Key Performance Indicators</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-md">
              {isLoading ? (
                <div className="bg-surface p-md rounded-xl border border-outline-variant animate-pulse h-[116px] flex flex-col justify-between">
                  <div className="h-4 bg-surface-container-high rounded w-2/3"></div>
                  <div className="h-8 bg-surface-container-high rounded w-1/2"></div>
                  <div className="h-3 bg-surface-container-high rounded w-3/4"></div>
                </div>
              ) : (
                <div className="bg-surface p-md rounded-xl border border-outline-variant hover:-translate-y-1 transition-transform h-[116px]">
                  <p className="font-label-sm text-label-sm text-secondary mb-2 flex items-center gap-1"><span className="material-symbols-outlined text-base">group</span> Total Users</p>
                  <p className="font-headline-md text-headline-md text-on-surface">{(overview?.total_users || 0).toLocaleString()}</p>
                  {formatTrend(overview?.users_change)}
                </div>
              )}

              {isLoading ? (
                <div className="bg-surface p-md rounded-xl border border-outline-variant animate-pulse h-[116px] flex flex-col justify-between">
                  <div className="h-4 bg-surface-container-high rounded w-2/3"></div>
                  <div className="h-8 bg-surface-container-high rounded w-1/2"></div>
                  <div className="h-3 bg-surface-container-high rounded w-3/4"></div>
                </div>
              ) : (
                <div className="bg-surface p-md rounded-xl border border-outline-variant hover:-translate-y-1 transition-transform h-[116px]">
                  <p className="font-label-sm text-label-sm text-secondary mb-2 flex items-center gap-1"><span className="material-symbols-outlined text-base">bolt</span> Sessions</p>
                  <p className="font-headline-md text-headline-md text-on-surface">{(overview?.total_charging_sessions || 0).toLocaleString()}</p>
                  {formatTrend(overview?.sessions_change)}
                </div>
              )}

              {isLoading ? (
                <div className="bg-surface p-md rounded-xl border border-outline-variant animate-pulse h-[116px] flex flex-col justify-between">
                  <div className="h-4 bg-surface-container-high rounded w-2/3"></div>
                  <div className="h-8 bg-surface-container-high rounded w-1/2"></div>
                  <div className="h-3 bg-surface-container-high rounded w-3/4"></div>
                </div>
              ) : (
                <div className="bg-surface p-md rounded-xl border border-outline-variant hover:-translate-y-1 transition-transform h-[116px]">
                  <p className="font-label-sm text-label-sm text-secondary mb-2 flex items-center gap-1"><span className="material-symbols-outlined text-base">star</span> Avg Rating</p>
                  <p className="font-headline-md text-headline-md text-on-surface">{`${overview?.average_feedback_rating?.toFixed(1) || '0.0'}/5`}</p>
                  {formatTrend(overview?.feedback_change)}
                </div>
              )}

              {isLoading ? (
                <div className="bg-surface p-md rounded-xl border border-outline-variant animate-pulse h-[116px] flex flex-col justify-between">
                  <div className="h-4 bg-surface-container-high rounded w-2/3"></div>
                  <div className="h-8 bg-surface-container-high rounded w-1/2"></div>
                  <div className="h-3 bg-surface-container-high rounded w-3/4"></div>
                </div>
              ) : (
                <div className="bg-surface p-md rounded-xl border border-outline-variant hover:-translate-y-1 transition-transform h-[116px]">
                  <p className="font-label-sm text-label-sm text-secondary mb-2 flex items-center gap-1"><span className="material-symbols-outlined text-base">energy_savings_leaf</span> Energy Saved</p>
                  <p className="font-headline-md text-headline-md text-on-surface">{`${overview?.total_energy_delivered?.toLocaleString() || 0} kWh`}</p>
                  {formatTrend(overview?.energy_change)}
                </div>
              )}

              {isLoading ? (
                <div className="bg-surface p-md rounded-xl border border-outline-variant animate-pulse h-[116px] flex flex-col justify-between">
                  <div className="h-4 bg-surface-container-high rounded w-2/3"></div>
                  <div className="h-8 bg-surface-container-high rounded w-1/2"></div>
                  <div className="h-3 bg-surface-container-high rounded w-3/4"></div>
                </div>
              ) : (
                <div className="bg-surface p-md rounded-xl border border-outline-variant hover:-translate-y-1 transition-transform h-[116px]">
                  <p className="font-label-sm text-label-sm text-secondary mb-2 flex items-center gap-1"><span className="material-symbols-outlined text-base">forum</span> Feedback</p>
                  <p className="font-headline-md text-headline-md text-on-surface">{(overview?.total_feedback || 0).toLocaleString()}</p>
                  {formatTrend(overview?.feedback_change)}
                </div>
              )}

              {isLoading ? (
                <div className="bg-surface p-md rounded-xl border border-outline-variant animate-pulse h-[116px] flex flex-col justify-between">
                  <div className="h-4 bg-surface-container-high rounded w-2/3"></div>
                  <div className="h-8 bg-surface-container-high rounded w-1/2"></div>
                  <div className="h-3 bg-surface-container-high rounded w-3/4"></div>
                </div>
              ) : (
                <div className="bg-surface p-md rounded-xl border border-outline-variant hover:-translate-y-1 transition-transform h-[116px]">
                  <p className="font-label-sm text-label-sm text-secondary mb-2 flex items-center gap-1"><span className="material-symbols-outlined text-base">warning</span> Complaints</p>
                  <p className="font-headline-md text-headline-md text-on-surface">{(overview?.total_complaints || 0).toLocaleString()}</p>
                  {formatTrend(overview?.complaints_change, true)}
                </div>
              )}
            </div>
          </section>

          <section className="bg-surface border border-outline-variant rounded-xl p-lg min-h-[220px]">
            <div className="flex justify-between items-center mb-md">
              <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">lightbulb</span>
                AI Analytics Insights
              </h3>
              <button 
                onClick={refreshAnalyticsInsights}
                disabled={isInsightsLoading}
                className="text-secondary hover:text-primary transition-colors disabled:opacity-50"
              >
                <span className={`material-symbols-outlined ${isInsightsLoading ? 'animate-spin' : ''}`}>sync</span>
              </button>
            </div>
            
            {isInsightsLoading ? (
               <div className="flex space-x-2 justify-center items-center py-8 h-[140px]" id="insights-three-dot-loader">
                 <div className="h-2.5 w-2.5 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                 <div className="h-2.5 w-2.5 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                 <div className="h-2.5 w-2.5 bg-primary rounded-full animate-bounce"></div>
               </div>
            ) : insightsError ? (
               <div className="text-error bg-error-container p-md rounded-lg">
                 <p>{insightsError}</p>
                 <button onClick={refreshAnalyticsInsights} className="text-sm font-semibold hover:underline mt-2">Retry</button>
               </div>
            ) : (
               <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
                 {analyticsInsights?.trends && analyticsInsights.trends.length > 0 && (
                   <div>
                     <h4 className="font-label-md text-secondary uppercase tracking-widest mb-2 flex items-center gap-1">
                       <span className="material-symbols-outlined text-sm">trending_up</span> Positive Trends
                     </h4>
                     <ul className="list-disc pl-5 space-y-1 text-on-surface font-body-md">
                       {analyticsInsights.trends.slice(0, 3).map((t, i) => <li key={i}>{t}</li>)}
                     </ul>
                   </div>
                 )}
                 {analyticsInsights?.anomalies && analyticsInsights.anomalies.length > 0 && (
                   <div>
                     <h4 className="font-label-md text-secondary uppercase tracking-widest mb-2 flex items-center gap-1 text-error">
                       <span className="material-symbols-outlined text-sm">error</span> Risk Indicators
                     </h4>
                     <ul className="list-disc pl-5 space-y-1 text-on-surface font-body-md">
                       {analyticsInsights.anomalies.slice(0, 3).map((a, i) => <li key={i}>{a}</li>)}
                     </ul>
                   </div>
                 )}
                 {analyticsInsights?.recommendations && analyticsInsights.recommendations.length > 0 && (
                   <div>
                     <h4 className="font-label-md text-secondary uppercase tracking-widest mb-2 flex items-center gap-1 text-primary">
                       <span className="material-symbols-outlined text-sm">insights</span> Opportunities
                     </h4>
                     <ul className="list-disc pl-5 space-y-1 text-on-surface font-body-md">
                       {analyticsInsights.recommendations.slice(0, 3).map((r, i) => <li key={i}>{r}</li>)}
                     </ul>
                   </div>
                 )}
               </div>
            )}
          </section>

          {/* Charts Section */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <div className="bg-surface border border-outline-variant rounded-xl p-lg h-80 flex flex-col">
              <div className="flex justify-between items-center mb-md">
                <h3 className="font-label-md text-label-md font-semibold text-on-surface">Feedback Trends</h3>
                <button className="text-secondary hover:text-on-surface"><span className="material-symbols-outlined">more_horiz</span></button>
              </div>
              <div className="flex-1 w-full bg-surface-container-low rounded-lg relative overflow-hidden flex items-center justify-center h-[216px]">
                {isLoading ? (
                  <div className="w-full h-full flex flex-col justify-end p-4 gap-2 animate-pulse">
                    <div className="flex justify-between items-end gap-2 h-4/5">
                      <div className="bg-surface-container-high rounded w-full h-[30%]"></div>
                      <div className="bg-surface-container-high rounded w-full h-[60%]"></div>
                      <div className="bg-surface-container-high rounded w-full h-[45%]"></div>
                      <div className="bg-surface-container-high rounded w-full h-[85%]"></div>
                      <div className="bg-surface-container-high rounded w-full h-[70%]"></div>
                      <div className="bg-surface-container-high rounded w-full h-[95%]"></div>
                    </div>
                    <div className="h-4 bg-surface-container-high rounded w-full"></div>
                  </div>
                ) : error ? (
                  <span className="text-error font-label-md">{error}</span>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={feedbackData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                      <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                      <Line type="monotone" dataKey="value" stroke="#006e2f" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
            
            <div className="bg-surface border border-outline-variant rounded-xl p-lg h-80 flex flex-col">
              <div className="flex justify-between items-center mb-md">
                <h3 className="font-label-md text-label-md font-semibold text-on-surface">Complaint Resolution</h3>
                <button className="text-secondary hover:text-on-surface"><span className="material-symbols-outlined">more_horiz</span></button>
              </div>
              <div className="flex-1 w-full bg-surface-container-low rounded-lg relative overflow-hidden flex items-center justify-center h-[216px]">
                {isLoading ? (
                  <div className="w-full h-full flex flex-col justify-end p-4 gap-2 animate-pulse">
                    <div className="flex justify-between items-end gap-2 h-4/5">
                      <div className="bg-surface-container-high rounded w-full h-[50%]"></div>
                      <div className="bg-surface-container-high rounded w-full h-[30%]"></div>
                      <div className="bg-surface-container-high rounded w-full h-[75%]"></div>
                      <div className="bg-surface-container-high rounded w-full h-[40%]"></div>
                    </div>
                    <div className="h-4 bg-surface-container-high rounded w-full"></div>
                  </div>
                ) : error ? (
                  <span className="text-error font-label-md">{error}</span>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={complaintData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                      <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} cursor={{ fill: '#f1f5f9' }} />
                      <Bar dataKey="value" fill="#006e2f" radius={[4, 4, 0, 0]} barSize={32} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </section>
        </div>

        {/* Right Sidebar (Actions & Timeline) */}
        <div className="space-y-xl">
          {/* Quick Actions */}
          <section className="bg-surface border border-outline-variant rounded-xl p-lg">
            <h3 className="font-label-md text-label-md text-secondary uppercase tracking-widest mb-md">Quick Actions</h3>
            <div className="space-y-sm">
              <button className="w-full bg-primary text-on-primary py-3 px-4 rounded-lg font-label-md text-label-md flex justify-center items-center gap-2 hover:bg-primary/90 transition-colors shadow-sm">
                <span className="material-symbols-outlined text-sm">summarize</span> Generate Report
              </button>
              <button className="w-full bg-surface border border-outline-variant text-on-surface py-3 px-4 rounded-lg font-label-md text-label-md flex justify-center items-center gap-2 hover:bg-surface-container-low transition-colors">
                <span className="material-symbols-outlined text-sm">assignment_late</span> View Complaints
              </button>
              <button className="w-full bg-surface border border-outline-variant text-on-surface py-3 px-4 rounded-lg font-label-md text-label-md flex justify-center items-center gap-2 hover:bg-surface-container-low transition-colors">
                <span className="material-symbols-outlined text-sm">forum</span> Manage Feedback
              </button>
            </div>
          </section>

          {/* Recent Activity */}
          <section className="bg-surface border border-outline-variant rounded-xl p-lg">
            <h3 className="font-label-md text-label-md text-secondary uppercase tracking-widest mb-md flex justify-between items-center">
              Recent Activity
              <a className="text-primary hover:underline lowercase normal-case text-xs" href="#">View all</a>
            </h3>
            
            {isLoading ? (
              <div className="space-y-4 animate-pulse">
                <div className="h-12 bg-surface-container-high rounded w-full"></div>
                <div className="h-12 bg-surface-container-high rounded w-full"></div>
                <div className="h-12 bg-surface-container-high rounded w-full"></div>
              </div>
            ) : error ? (
              <div className="p-4 text-center text-error font-body-sm">{error}</div>
            ) : recentActivity?.activities?.length === 0 ? (
              <div className="p-4 text-center text-secondary font-body-sm">No recent activity.</div>
            ) : (
              <div className="relative pl-4 border-l border-outline-variant space-y-6">
                {recentActivity?.activities?.map((activity) => (
                  <div key={activity.id} className="relative">
                    <div className={`absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full border-2 border-surface ${getActivityIconAndColor(activity.type)}`}></div>
                    <p className="font-body-sm text-body-sm text-on-surface font-medium mb-1">{activity.title}</p>
                    {activity.description && (
                      <p className="font-body-sm text-body-sm text-secondary">{activity.description}</p>
                    )}
                    <p className="font-label-sm text-label-sm text-tertiary mt-1">
                      {new Date(activity.timestamp).toLocaleString(undefined, { 
                        month: 'short', 
                        day: 'numeric', 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
