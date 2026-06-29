import { useRef } from 'react';
import { useFeedback } from '../hooks/useFeedback';
import { format, isToday, isYesterday } from 'date-fns';

interface FilterSelectProps {
  icon: string;
  value: string | number;
  onChange: (val: string) => void;
  options: { value: string; label: string }[];
  widthClass?: string;
}

function FilterSelect({ icon, value, onChange, options, widthClass }: FilterSelectProps) {
  return (
    <div className="flex items-center gap-2 border border-outline-variant rounded-lg px-3 py-2 bg-surface-container-lowest">
      <span className="material-symbols-outlined text-secondary text-sm">{icon}</span>
      <select 
        className={`bg-transparent border-none font-body-sm text-on-surface focus:outline-none cursor-pointer pr-8 py-0 ${widthClass || 'w-32'}`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}

export function FeedbackPage() {
  const rowRefs = useRef<Map<string, HTMLTableRowElement>>(new Map());
  const {
    data,
    total,
    page,
    setPage,
    size,
    loadingList,
    errorList,
    filters,
    setFilters,
    selectedFeedbackId,
    setSelectedFeedbackId,
    selectedFeedback,
    loadingDetail,
    loadingAI,
    aiError,
    analyzeFeedbackItem,
    refresh
  } = useFeedback();

  const totalPages = Math.ceil(total / size) || 1;

  const formatCategory = (category: string | null | undefined): string => {
    if (!category) return 'General';
    return category
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  const formatSmartDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    if (isToday(date)) return `Today, ${format(date, 'HH:mm')}`;
    if (isYesterday(date)) return `Yesterday, ${format(date, 'HH:mm')}`;
    return format(date, 'MMM dd, yyyy');
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1.5">
        <div className={`flex ${rating <= 2 ? 'text-error' : rating <= 3 ? 'text-warning' : 'text-primary'}`}>
          {[1, 2, 3, 4, 5].map((star) => (
            <span 
              key={star} 
              className={`material-symbols-outlined text-sm ${star > rating ? 'text-surface-variant' : ''}`} 
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              star
            </span>
          ))}
        </div>
        <span className="font-label-sm text-secondary">{rating}/5</span>
      </div>
    );
  };

  const renderCategory = (category: string | null | undefined) => {
    const label = formatCategory(category);
    let colorClass = 'bg-secondary-container text-on-secondary-container';
    let dotClass = 'bg-secondary';
    if (label.toLowerCase().includes('hardware') || label.toLowerCase().includes('charger')) {
      colorClass = 'bg-error-container text-on-error-container';
      dotClass = 'bg-error';
    } else if (label.toLowerCase().includes('software') || label.toLowerCase().includes('app')) {
      colorClass = 'bg-primary-container text-on-primary-container';
      dotClass = 'bg-primary';
    } else if (label.toLowerCase().includes('billing') || label.toLowerCase().includes('payment')) {
      colorClass = 'bg-tertiary-container text-on-tertiary-container';
      dotClass = 'bg-tertiary';
    }

    return (
      <span className={`px-2 py-1 ${colorClass} rounded-md font-label-sm text-label-sm inline-flex items-center gap-1`}>
        <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`}></span> {label}
      </span>
    );
  };

  const renderSentimentBadge = (sentiment?: string) => {
    if (!sentiment) return <span className="text-secondary font-body-sm text-sm italic">Not analyzed</span>;
    const lower = sentiment.toLowerCase();
    if (lower.includes('pos')) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-green-500/10 text-green-500 font-label-sm text-sm">
          😊 Positive
        </span>
      );
    } else if (lower.includes('neg')) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-error-container text-error font-label-sm text-sm">
          ☹ Negative
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-secondary-container text-secondary font-label-sm text-sm">
          😐 Neutral
        </span>
      );
    }
  };

  return (
    <main className="h-full flex flex-col overflow-hidden">

      {/*  TopNavBar Component  */}
      <header className="bg-[#000000] fixed top-0 right-0 w-[calc(100%-16rem)] h-16 border-b border-outline-variant dark:border-outline z-40 flex justify-between items-center px-lg">
        <div className="flex-1 flex items-center gap-4">
          <h2 className="font-headline-sm text-headline-sm font-semibold text-white">Customer Feedback</h2>
          {loadingList && <span className="material-symbols-outlined animate-spin text-white/70 text-sm">progress_activity</span>}
        </div>
        <div className="flex items-center gap-6">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-white/60">search</span>
            <input 
              className="pl-10 pr-4 py-2 bg-zinc-900 border border-zinc-800 rounded-full text-white placeholder-zinc-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-64 font-body-sm transition-all duration-200" 
              placeholder="Search by phone..." 
              type="text"
              value={filters.searchQuery}
              onChange={(e) => setFilters(f => ({ ...f, searchQuery: e.target.value }))}
            />
          </div>
          <div className="flex items-center gap-3 cursor-pointer hover:bg-white/10 p-2 rounded-lg transition-colors">
            <div className="w-8 h-8 rounded-full bg-tertiary-container overflow-hidden">
              <div className="w-full h-full bg-primary-container text-on-primary-container flex items-center justify-center font-bold">
                AD
              </div>
            </div>
            <span className="font-label-md text-label-md text-white">Admin</span>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden p-lg gap-6 min-h-0">
        {/*  Left Data Area  */}
        <div className="flex-1 flex flex-col overflow-hidden min-h-0">
          {/*  Filter Bar  */}
          <div className="bg-surface p-md rounded-xl border border-outline-variant mb-lg flex flex-wrap gap-4 items-center justify-between">
            <div className="flex flex-wrap gap-4 items-center">
              
              <FilterSelect 
                icon="calendar_today"
                value={filters.dateRange || ''}
                onChange={(val) => setFilters(f => ({ ...f, dateRange: val }))}
                options={[
                  { value: '', label: 'All Time' },
                  { value: '30days', label: 'Last 30 Days' }
                ]}
                widthClass="w-32"
              />

              <FilterSelect 
                icon="star"
                value={filters.rating || ''}
                onChange={(val) => setFilters(f => ({ ...f, rating: val ? Number(val) : undefined }))}
                options={[
                  { value: '', label: 'All Ratings' },
                  { value: '5', label: '5 Stars' },
                  { value: '4', label: '4 Stars' },
                  { value: '3', label: '3 Stars' },
                  { value: '2', label: '2 Stars' },
                  { value: '1', label: '1 Star' }
                ]}
                widthClass="w-32"
              />

              <FilterSelect 
                icon="category"
                value={filters.issueCategory || ''}
                onChange={(val) => setFilters(f => ({ ...f, issueCategory: val || undefined }))}
                options={[
                  { value: '', label: 'All Categories' },
                  { value: 'charger_issue', label: 'Charger' },
                  { value: 'app_issue', label: 'App' },
                  { value: 'facility_issue', label: 'Facility' },
                  { value: 'general', label: 'General' },
                  { value: 'other', label: 'Other' }
                ]}
                widthClass="w-40"
              />

              <button 
                onClick={() => setFilters({ searchQuery: '' })}
                className="text-secondary hover:text-primary font-label-sm text-label-sm transition-colors flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-sm">close</span> Reset
              </button>
            </div>
            <div className="flex gap-3">
              <button 
                onClick={refresh}
                className="flex items-center gap-2 px-4 py-2 border border-outline-variant bg-surface-container-lowest rounded-lg hover:bg-surface-container-low transition-colors font-label-md text-label-md text-on-surface"
              >
                <span className="material-symbols-outlined text-sm">refresh</span> Refresh
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded-lg hover:bg-primary-fixed-dim hover:text-on-primary-fixed transition-colors font-label-md text-label-md">
                <span className="material-symbols-outlined text-sm">bar_chart</span> Report
              </button>
            </div>
          </div>
          
          {/*  Data Table  */}
          <div className="bg-surface rounded-xl border border-outline-variant flex-1 flex flex-col overflow-hidden min-h-0">
            <div className="overflow-x-auto overflow-y-auto flex-1 min-h-0">
              <table className="w-full text-left border-collapse">
                <thead className="sticky top-0 z-10">
                  <tr className="border-b border-outline-variant bg-surface-container-low">
                    <th className="p-4 font-label-sm text-label-sm text-secondary font-medium">Customer</th>
                    <th className="p-4 font-label-sm text-label-sm text-secondary font-medium">AI Sentiment</th>
                    <th className="p-4 font-label-sm text-label-sm text-secondary font-medium w-1/3">Feedback Comment</th>
                    <th className="p-4 font-label-sm text-label-sm text-secondary font-medium">Rating</th>
                    <th className="p-4 font-label-sm text-label-sm text-secondary font-medium">Category</th>
                    <th className="p-4 font-label-sm text-label-sm text-secondary font-medium">Charger Name</th>
                    <th className="p-4 font-label-sm text-label-sm text-secondary font-medium">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant">
                  {errorList && (
                    <tr>
                      <td colSpan={7} className="p-8 text-center text-error font-body-sm">{errorList}</td>
                    </tr>
                  )}
                  {!errorList && data.length === 0 && !loadingList && (
                    <tr>
                      <td colSpan={7} className="p-8 text-center text-secondary font-body-sm">No feedback records found.</td>
                    </tr>
                  )}
                  {data.map((item) => (
                    <tr 
                      key={item.id}
                      ref={(el) => {
                        if (el) rowRefs.current.set(item.id, el);
                        else rowRefs.current.delete(item.id);
                      }}
                      onClick={() => {
                        setSelectedFeedbackId(item.id);
                        const el = rowRefs.current.get(item.id);
                        if (el) {
                          el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        }
                      }}
                      className={`hover:bg-surface-container-lowest transition-colors cursor-pointer ${
                        selectedFeedbackId === item.id 
                          ? 'bg-surface-container-lowest border-l-4 border-l-primary' 
                          : 'border-l-4 border-transparent'
                      }`}
                    >
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full ${item.rating <= 2 ? 'bg-error-container text-on-error-container' : 'bg-secondary-container text-on-secondary-container'} flex items-center justify-center text-secondary`}>
                            <span className="material-symbols-outlined text-[18px]">person</span>
                          </div>
                          <div>
                            <span className="font-body-sm font-medium text-on-surface block">{item.user_phone || 'N/A'}</span>
                            {item.user_name && <span className="font-body-sm text-secondary text-[12px]">{item.user_name}</span>}
                          </div>
                        </div>
                      </td>
                      <td className="p-4">
                        {renderSentimentBadge(item.ai_analysis?.sentiment)}
                      </td>
                      <td className="p-4">
                        <p className="font-body-sm text-on-surface-variant truncate max-w-xs">{item.feedback_comment || '-'}</p>
                      </td>
                      <td className="p-4">
                        {renderStars(item.rating)}
                      </td>
                      <td className="p-4">
                        {renderCategory(item.issue_category)}
                      </td>
                      <td className="p-4 font-body-sm text-secondary font-mono">{item.charger_name || '-'}</td>
                      <td className="p-4 font-body-sm text-secondary">{item.created_at ? formatSmartDate(item.created_at) : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Footer */}
            <div className="border-t border-outline-variant p-4 flex items-center justify-between bg-surface-bright mt-auto">
              <p className="font-body-sm text-body-sm text-secondary">
                Showing {Math.min((page - 1) * size + 1, total)}-{Math.min(page * size, total)} of {total} feedback records
              </p>
              <div className="flex gap-2">
                <button 
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-1 rounded text-secondary hover:bg-surface-container transition-colors disabled:opacity-50"
                >
                  <span className="material-symbols-outlined text-[20px]">chevron_left</span>
                </button>
                <button 
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages || total === 0}
                  className="p-1 rounded text-on-surface hover:bg-surface-container transition-colors disabled:opacity-50"
                >
                  <span className="material-symbols-outlined text-[20px]">chevron_right</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* DETAIL PANEL SECTION */}
        {selectedFeedbackId && (
          <div className="w-[400px] xl:w-[450px] shrink-0 bg-surface-container-lowest border border-outline-variant rounded-xl flex flex-col overflow-hidden shadow-md relative">
            
            {loadingDetail && !selectedFeedback && (
              <div className="absolute inset-0 bg-surface/50 z-10 flex items-center justify-center">
                <span className="material-symbols-outlined animate-spin text-primary text-3xl">progress_activity</span>
              </div>
            )}

            {/* Detail Header */}
            <div className="p-5 border-b border-outline-variant flex items-start justify-between bg-surface-bright">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-headline-md text-[20px] leading-tight font-bold text-on-surface">Feedback Details</h3>
                  {selectedFeedback && renderCategory(selectedFeedback.issue_category)}
                </div>
                <p className="font-body-sm text-body-sm text-secondary">
                  {selectedFeedback ? `Submitted ${selectedFeedback.created_at ? formatSmartDate(selectedFeedback.created_at) : 'N/A'}` : 'Loading...'}
                </p>
              </div>
              <button 
                onClick={() => setSelectedFeedbackId(null)}
                className="text-secondary hover:text-on-surface p-1 rounded-md hover:bg-surface-container transition-colors"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {selectedFeedback && (
              <div className="flex-1 overflow-y-auto p-5 space-y-6">
                
                {/* Customer Context */}
                <div className="p-4 bg-surface rounded-lg border border-outline-variant/50">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center text-secondary">
                      <span className="material-symbols-outlined text-[24px]">person</span>
                    </div>
                    <div>
                      <div className="font-label-md text-label-md font-semibold text-on-surface">{selectedFeedback.user_phone || 'N/A'}</div>
                      <div className="font-body-sm text-body-sm text-secondary flex items-center gap-1 mt-0.5">
                        <span className="material-symbols-outlined text-[14px]">call</span> {selectedFeedback.user_name || 'N/A'}
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-outline-variant/50 font-body-sm text-body-sm">
                    <div>
                      <span className="text-secondary block mb-1 font-label-sm text-label-sm">Category</span>
                      {renderCategory(selectedFeedback.issue_category)}
                    </div>
                    <div>
                      <span className="text-secondary block mb-1 font-label-sm text-label-sm">Rating</span>
                      {renderStars(selectedFeedback.rating)}
                    </div>
                  </div>
                </div>

                {/* Session Context */}
                {selectedFeedback.charging_session && (
                  <div>
                    <h4 className="font-label-md text-label-md font-semibold text-on-surface mb-2">Charging Session</h4>
                    <div className="p-4 bg-surface rounded-lg border border-outline-variant/50 font-body-sm text-body-sm grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-secondary block mb-1">Charger</span>
                        <span className="font-medium text-on-surface font-mono">{selectedFeedback.charger_name || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="text-secondary block mb-1">Energy Delivered</span>
                        <span className="font-medium text-on-surface">{selectedFeedback.charging_session.energy_kwh?.toFixed(2) ?? 'N/A'} kWh</span>
                      </div>
                      <div>
                        <span className="text-secondary block mb-1">Total Cost</span>
                        <span className="font-medium text-on-surface">${selectedFeedback.charging_session.amount_paid?.toFixed(2) ?? 'N/A'}</span>
                      </div>
                      <div>
                        <span className="text-secondary block mb-1">Status</span>
                        <span className={`font-medium ${selectedFeedback.charging_session.status === 'completed' ? 'text-primary' : 'text-error'}`}>
                          {selectedFeedback.charging_session.status?.toUpperCase() || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Comments */}
                <div>
                  <h4 className="font-label-md text-label-md font-semibold text-on-surface mb-2">Feedback Comment</h4>
                  <div className="bg-surface-container-low p-4 rounded-lg font-body-sm text-body-sm text-on-surface-variant leading-relaxed min-h-[100px]">
                    {selectedFeedback.feedback_comment ? `"${selectedFeedback.feedback_comment}"` : <span className="text-secondary italic">No comment provided.</span>}
                  </div>
                </div>

                {/* AI Analysis Section */}
                <hr className="border-outline-variant/60 my-4" />
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <h4 className="font-label-md text-label-md font-semibold text-on-surface flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-primary text-lg">auto_awesome</span>
                      AI Analysis
                    </h4>
                    {selectedFeedback.ai_analysis && (
                      <button
                        onClick={() => analyzeFeedbackItem(true)}
                        disabled={loadingAI}
                        className="text-secondary hover:text-primary transition-colors font-label-sm text-sm flex items-center gap-1 disabled:opacity-50"
                      >
                        <span className={`material-symbols-outlined text-sm ${loadingAI ? 'animate-spin' : ''}`}>sync</span> Reanalyze
                      </button>
                    )}
                  </div>

                  {loadingAI ? (
                    <div className="flex flex-col items-center justify-center p-lg bg-surface border border-outline-variant/60 rounded-lg min-h-[140px] text-center">
                      <span className="text-secondary font-body-sm text-sm mb-2">Analyzing feedback...</span>
                      <div className="flex space-x-1.5 justify-center items-center">
                        <div className="h-2.5 w-2.5 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                        <div className="h-2.5 w-2.5 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                        <div className="h-2.5 w-2.5 bg-primary rounded-full animate-bounce"></div>
                      </div>
                    </div>
                  ) : aiError ? (
                    <div className="bg-error-container text-on-error-container p-3 rounded-lg flex flex-col items-start border border-error/20">
                      <p className="font-body-sm text-sm mb-2">{aiError}</p>
                      <button onClick={() => analyzeFeedbackItem(true)} className="text-sm font-semibold hover:underline text-primary">Retry</button>
                    </div>
                  ) : !selectedFeedback.ai_analysis ? (
                    <div className="flex flex-col items-center justify-center p-lg bg-surface border border-dashed border-outline-variant rounded-lg min-h-[140px] text-center">
                      <p className="font-body-sm text-sm text-secondary mb-3">AI Analysis not generated yet.</p>
                      <button
                        onClick={() => analyzeFeedbackItem(false)}
                        className="px-4 py-1.5 bg-primary text-on-primary rounded font-label-sm text-sm hover:bg-primary-fixed-dim transition-colors"
                      >
                        Analyze
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="p-4 bg-surface rounded-lg border border-outline-variant/50 font-body-sm text-sm space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <span className="text-secondary block mb-1 text-xs font-label-sm uppercase tracking-wider">Sentiment</span>
                            {renderSentimentBadge(selectedFeedback.ai_analysis.sentiment)}
                          </div>
                          <div>
                            <span className="text-secondary block mb-1 text-xs font-label-sm uppercase tracking-wider">Priority</span>
                            <span className={`inline-flex px-2 py-0.5 rounded font-label-sm text-sm font-semibold ${
                              selectedFeedback.ai_analysis.priority.toLowerCase() === 'critical' ? 'bg-error-container text-error' :
                              selectedFeedback.ai_analysis.priority.toLowerCase() === 'high' ? 'bg-orange-500/10 text-orange-500' :
                              selectedFeedback.ai_analysis.priority.toLowerCase() === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                              'bg-secondary-container text-secondary'
                            }`}>
                              {selectedFeedback.ai_analysis.priority}
                            </span>
                          </div>
                          <div>
                            <span className="text-secondary block mb-1 text-xs font-label-sm uppercase tracking-wider">Suggested Category</span>
                            <span className="inline-flex px-2 py-0.5 rounded bg-primary-container text-on-primary-container font-label-sm text-sm">
                              {selectedFeedback.ai_analysis.category}
                            </span>
                          </div>
                          <div>
                            <span className="text-secondary block mb-1 text-xs font-label-sm uppercase tracking-wider">Confidence</span>
                            <span className="font-semibold text-on-surface">
                              {Math.round(selectedFeedback.ai_analysis.confidence_score * 100)}%
                            </span>
                          </div>
                        </div>

                        <div className="pt-3 border-t border-outline-variant/50">
                          <span className="text-secondary block mb-1 text-xs font-label-sm uppercase tracking-wider">Summary</span>
                          <p className="text-on-surface leading-relaxed italic">"{selectedFeedback.ai_analysis.summary}"</p>
                        </div>

                        <div className="pt-3 border-t border-outline-variant/50">
                          <span className="text-secondary block mb-1 text-xs font-label-sm uppercase tracking-wider">Suggested Action</span>
                          <p className="text-on-surface-variant font-medium">{selectedFeedback.ai_analysis.suggested_action}</p>
                        </div>
                      </div>

                      <div className="flex justify-between items-center text-[11px] text-secondary px-1">
                        <span>Model: {selectedFeedback.ai_analysis.model_name || 'Gemini'} {selectedFeedback.ai_analysis.model_version || ''}</span>
                        <span>Analyzed {selectedFeedback.ai_analysis.analyzed_at ? formatSmartDate(selectedFeedback.ai_analysis.analyzed_at) : 'N/A'}</span>
                      </div>
                    </div>
                  )}
                </div>

              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
