import { useState, useEffect } from 'react';
import { useSettings } from '../hooks/useSettings';

export function SettingsPage() {
  const { settingsMap, loading, error, updateSettings } = useSettings();
  
  // Local state for the form
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [toast, setToast] = useState<{ message: string; show: boolean } | null>(null);

  // Sync with backend settings map when it loads
  useEffect(() => {
    if (!loading && Object.keys(settingsMap).length > 0) {
      setFormData(settingsMap);
    }
  }, [settingsMap, loading]);

  const handleChange = (key: string, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updates = Object.keys(formData).map((key) => ({
        setting_key: key,
        setting_value: formData[key],
      }));
      await updateSettings({ settings: updates });
      setToast({ message: 'Your workspace preferences have been updated.', show: true });
      setTimeout(() => setToast(null), 4000);
    } catch (err) {
      console.error(err);
      setToast({ message: 'Failed to save settings.', show: true });
      setTimeout(() => setToast(null), 4000);
    } finally {
      setIsSaving(false);
    }
  };

  if (loading && Object.keys(formData).length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-background">
        <span className="material-symbols-outlined animate-spin text-primary text-4xl">
          progress_activity
        </span>
      </div>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto custom-scrollbar p-md sm:p-lg lg:p-xl bg-background scroll-smooth">
      <div className="max-w-[1280px] mx-auto w-full pb-margin">
        
        {/* Header Area */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-xl mt-sm">
          <div>
            <h2 className="font-headline-lg-mobile md:font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface">Settings</h2>
            <p className="font-body-md text-body-md text-secondary mt-1">Manage your workspace preferences and system configurations.</p>
          </div>
          <div className="flex shrink-0 gap-3">
            <button 
              onClick={() => setFormData(settingsMap)}
              className="px-4 py-2 font-label-md text-label-md bg-surface border border-outline text-on-surface hover:bg-surface-container-low rounded-lg transition-all active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              Discard
            </button>
            <button 
              onClick={handleSave}
              disabled={isSaving}
              className={`flex items-center justify-center gap-2 px-6 py-2 font-label-md text-label-md text-on-primary rounded-lg transition-all shadow-sm hover:shadow-md active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 min-w-[140px] ${
                isSaving ? 'bg-primary/80 cursor-not-allowed' : 'bg-primary hover:bg-on-primary-fixed-variant'
              }`}
            >
              <span className={`material-symbols-outlined text-[20px] ${isSaving ? 'hidden' : ''}`}>save</span>
              <span>{isSaving ? 'Saving...' : 'Save Changes'}</span>
              {isSaving && (
                <span className="material-symbols-outlined animate-spin text-[20px]">progress_activity</span>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-error-container text-on-error-container rounded-lg">
            {error}
          </div>
        )}

        {/* Settings Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
          
          {/* Left Column (Primary Settings) */}
          <div className="lg:col-span-8 flex flex-col gap-lg">
            
            {/* 1. Company Settings */}
            <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg shadow-sm">
              <div className="mb-md">
                <h3 className="font-headline-md text-[20px] leading-7 text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-[24px]">domain</span>
                  Company Settings
                </h3>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
                <div className="flex flex-col gap-xs">
                  <label className="font-label-sm text-label-sm text-on-surface-variant">Company Name</label>
                  <input 
                    className="font-body-md text-body-md px-4 py-[14px] bg-surface-container-lowest border border-outline-variant rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-shadow text-on-surface w-full" 
                    type="text" 
                    value={formData.company_name || ''} 
                    onChange={(e) => handleChange('company_name', e.target.value)}
                  />
                </div>
                <div className="flex flex-col gap-xs">
                  <label className="font-label-sm text-label-sm text-on-surface-variant">Industry</label>
                  <select 
                    className="font-body-md text-body-md px-4 py-[14px] bg-surface-container-lowest border border-outline-variant rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-shadow text-on-surface w-full appearance-none pr-10 bg-no-repeat bg-[position:right_12px_center]"
                    style={{ backgroundImage: "url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%235c6274%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')" }}
                    value={formData.company_industry || ''}
                    onChange={(e) => handleChange('company_industry', e.target.value)}
                  >
                    <option value="">Select Industry</option>
                    <option value="Energy Management">Energy Management</option>
                    <option value="Sustainability Tech">Sustainability Tech</option>
                    <option value="Utility Software">Utility Software</option>
                  </select>
                </div>
                <div className="flex flex-col gap-xs sm:col-span-2">
                  <label className="font-label-sm text-label-sm text-on-surface-variant">Primary Contact Email</label>
                  <input 
                    className="font-body-md text-body-md px-4 py-[14px] bg-surface-container-lowest border border-outline-variant rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-shadow text-on-surface w-full" 
                    type="email" 
                    value={formData.company_email || ''}
                    onChange={(e) => handleChange('company_email', e.target.value)}
                  />
                </div>
              </div>
            </section>

            {/* 2. Dashboard Preferences */}
            <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg shadow-sm">
              <div className="mb-md border-b border-outline-variant pb-sm">
                <h3 className="font-headline-md text-[20px] leading-7 text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-[24px]">tune</span>
                  Dashboard Preferences
                </h3>
              </div>
              <div className="flex flex-col gap-md">
                <div className="flex items-center justify-between py-2">
                  <div>
                    <h4 className="font-label-md text-label-md text-on-surface">Show Executive Summary</h4>
                    <p className="font-body-sm text-body-sm text-secondary mt-1">Display high-level metrics at the top of the dashboard.</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input 
                      className="sr-only peer" 
                      type="checkbox" 
                      checked={!!formData.dashboard_show_executive_summary}
                      onChange={(e) => handleChange('dashboard_show_executive_summary', e.target.checked)}
                    />
                    <div className="w-11 h-6 bg-surface-container-highest peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-md pt-sm border-t border-surface-container-high">
                  <div className="flex flex-col gap-xs">
                    <label className="font-label-sm text-label-sm text-on-surface-variant">Default Date Range</label>
                    <select 
                      className="font-body-md text-body-md px-4 py-[14px] bg-surface-container-lowest border border-outline-variant rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-on-surface w-full appearance-none pr-10 bg-no-repeat bg-[position:right_12px_center]"
                      style={{ backgroundImage: "url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%235c6274%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')" }}
                      value={formData.dashboard_default_date_range || 'Last 30 Days'}
                      onChange={(e) => handleChange('dashboard_default_date_range', e.target.value)}
                    >
                      <option value="Last 7 Days">Last 7 Days</option>
                      <option value="Last 30 Days">Last 30 Days</option>
                      <option value="This Month">This Month</option>
                      <option value="Year to Date">Year to Date</option>
                    </select>
                  </div>
                  <div className="flex flex-col gap-xs">
                    <label className="font-label-sm text-label-sm text-on-surface-variant">Language</label>
                    <select 
                      className="font-body-md text-body-md px-4 py-[14px] bg-surface-container-lowest border border-outline-variant rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-on-surface w-full appearance-none pr-10 bg-no-repeat bg-[position:right_12px_center]"
                      style={{ backgroundImage: "url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%235c6274%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')" }}
                      value={formData.dashboard_language || 'English (US)'}
                      onChange={(e) => handleChange('dashboard_language', e.target.value)}
                    >
                      <option value="English (US)">English (US)</option>
                      <option value="Spanish (ES)">Spanish (ES)</option>
                      <option value="French (FR)">French (FR)</option>
                    </select>
                  </div>
                </div>
              </div>
            </section>

            {/* 4 & 5. Operational Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
              
              {/* Complaint Management */}
              <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg shadow-sm flex flex-col">
                <div className="mb-md">
                  <h3 className="font-headline-md text-[20px] leading-7 text-on-surface flex items-center gap-2">
                    <span className="material-symbols-outlined text-secondary text-[24px]">rule</span>
                    Complaint Handling
                  </h3>
                </div>
                <div className="flex-1 flex flex-col justify-between gap-md">
                  <div className="flex items-center justify-between">
                    <span className="font-label-md text-label-md text-on-surface">Auto-assign tickets</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input 
                        className="sr-only peer" 
                        type="checkbox" 
                        checked={!!formData.complaint_auto_assign}
                        onChange={(e) => handleChange('complaint_auto_assign', e.target.checked)}
                      />
                      <div className="w-9 h-5 bg-surface-container-highest peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                  <div className="flex flex-col gap-xs">
                    <label className="font-label-sm text-label-sm text-on-surface-variant">Priority Threshold</label>
                    <select 
                      className="font-body-sm text-body-sm px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:outline-none focus:ring-2 focus:ring-primary w-full appearance-none"
                      value={formData.complaint_priority_threshold || 'High & Critical'}
                      onChange={(e) => handleChange('complaint_priority_threshold', e.target.value)}
                    >
                      <option value="Critical Only">Critical Only</option>
                      <option value="High & Critical">High & Critical</option>
                      <option value="All Priorities">All Priorities</option>
                    </select>
                  </div>
                </div>
              </section>

              {/* Report Settings */}
              <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg shadow-sm flex flex-col">
                <div className="mb-md">
                  <h3 className="font-headline-md text-[20px] leading-7 text-on-surface flex items-center gap-2">
                    <span className="material-symbols-outlined text-secondary text-[24px]">summarize</span>
                    Reporting
                  </h3>
                </div>
                <div className="flex-1 flex flex-col gap-md">
                  <div className="flex items-center justify-between">
                    <span className="font-label-md text-label-md text-on-surface">Auto-generate Weekly</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input 
                        className="sr-only peer" 
                        type="checkbox" 
                        checked={!!formData.report_auto_generate}
                        onChange={(e) => handleChange('report_auto_generate', e.target.checked)}
                      />
                      <div className="w-9 h-5 bg-surface-container-highest peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                  <div className="flex flex-col gap-xs mt-auto">
                    <label className="font-label-sm text-label-sm text-on-surface-variant">Recipients List</label>
                    <div className="flex gap-2">
                      <input 
                        className="font-body-sm text-body-sm px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:outline-none focus:ring-2 focus:ring-primary flex-1 min-w-0" 
                        placeholder="Add email..." 
                        type="text"
                        value={formData.report_recipients_list || ''}
                        onChange={(e) => handleChange('report_recipients_list', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </section>

            </div>
          </div>

          {/* Right Column (Secondary / Contextual Settings) */}
          <div className="lg:col-span-4 flex flex-col gap-lg">
            
            {/* 3. Notification Settings */}
            <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg shadow-sm">
              <div className="mb-md border-b border-outline-variant pb-sm">
                <h3 className="font-headline-md text-[20px] leading-7 text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-[24px]">notifications_active</span>
                  Notifications
                </h3>
              </div>
              <div className="flex flex-col gap-sm">
                <label className="flex items-start gap-3 p-2 hover:bg-surface-bright rounded-lg cursor-pointer transition-colors group">
                  <div className="relative flex items-center mt-1">
                    <input 
                      className="w-5 h-5 appearance-none border-2 border-outline rounded bg-surface-container-lowest checked:bg-primary checked:border-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1 transition-all cursor-pointer peer" 
                      type="checkbox"
                      checked={!!formData.notification_email_alerts}
                      onChange={(e) => handleChange('notification_email_alerts', e.target.checked)}
                    />
                    <span className="material-symbols-outlined absolute text-white text-[16px] left-[2px] top-[2px] pointer-events-none opacity-0 peer-checked:opacity-100 transition-opacity">check</span>
                  </div>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface group-hover:text-primary transition-colors">Email Alerts</p>
                    <p className="font-body-sm text-body-sm text-secondary">Daily summaries and updates.</p>
                  </div>
                </label>
                <label className="flex items-start gap-3 p-2 hover:bg-surface-bright rounded-lg cursor-pointer transition-colors group">
                  <div className="relative flex items-center mt-1">
                    <input 
                      className="w-5 h-5 appearance-none border-2 border-outline rounded bg-surface-container-lowest checked:bg-primary checked:border-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1 transition-all cursor-pointer peer" 
                      type="checkbox"
                      checked={!!formData.notification_push_alerts}
                      onChange={(e) => handleChange('notification_push_alerts', e.target.checked)}
                    />
                    <span className="material-symbols-outlined absolute text-white text-[16px] left-[2px] top-[2px] pointer-events-none opacity-0 peer-checked:opacity-100 transition-opacity">check</span>
                  </div>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface group-hover:text-primary transition-colors">Push Notifications</p>
                    <p className="font-body-sm text-body-sm text-secondary">Real-time alerts in browser.</p>
                  </div>
                </label>
                <label className="flex items-start gap-3 p-2 hover:bg-surface-bright rounded-lg cursor-pointer transition-colors group">
                  <div className="relative flex items-center mt-1">
                    <input 
                      className="w-5 h-5 appearance-none border-2 border-outline rounded bg-surface-container-lowest checked:bg-primary checked:border-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1 transition-all cursor-pointer peer" 
                      type="checkbox"
                      checked={!!formData.notification_sms_alerts}
                      onChange={(e) => handleChange('notification_sms_alerts', e.target.checked)}
                    />
                    <span className="material-symbols-outlined absolute text-white text-[16px] left-[2px] top-[2px] pointer-events-none opacity-0 peer-checked:opacity-100 transition-opacity">check</span>
                  </div>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface group-hover:text-primary transition-colors">SMS Alerts</p>
                    <p className="font-body-sm text-body-sm text-secondary">Only for critical complaints.</p>
                  </div>
                </label>
              </div>
            </section>

            {/* 7. System Information (Read-only) */}
            <section className="bg-surface-bright border border-outline-variant rounded-xl p-lg shadow-sm">
              <div className="mb-md">
                <h3 className="font-headline-md text-[20px] leading-7 text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-[24px]">info</span>
                  System Info
                </h3>
              </div>
              <ul className="flex flex-col font-body-sm text-body-sm divide-y divide-outline-variant border-t border-outline-variant">
                <li className="py-2 flex justify-between items-center">
                  <span className="text-secondary">Dashboard Version</span>
                  <span className="text-on-surface font-medium">v2.4.0</span>
                </li>
                <li className="py-2 flex justify-between items-center">
                  <span className="text-secondary">Backend Version</span>
                  <span className="text-on-surface font-medium">v1.8.2</span>
                </li>
                <li className="py-2 flex justify-between items-center">
                  <span className="text-secondary">Database Status</span>
                  <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-primary-container"></span> Connected</span>
                </li>
                <li className="py-2 flex justify-between items-center">
                  <span className="text-secondary">API Status</span>
                  <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-primary-container"></span> Operational</span>
                </li>
                <li className="py-2 flex justify-between items-center">
                  <span className="text-secondary">Last Sync</span>
                  <span className="text-on-surface font-medium">Just now</span>
                </li>
                <li className="py-2 pt-3 flex flex-col gap-1 border-b-0">
                  <div className="flex justify-between items-center">
                    <span className="text-secondary">Storage Usage</span>
                    <span className="text-on-surface font-medium">45.2 / 100 GB</span>
                  </div>
                  <div className="w-full bg-surface-container-high rounded-full h-1.5 mt-1 overflow-hidden">
                    <div className="bg-primary h-1.5 rounded-full" style={{ width: '45%' }}></div>
                  </div>
                </li>
              </ul>
            </section>

            {/* 8. Data Management */}
            <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg shadow-sm">
              <div className="mb-md">
                <h3 className="font-headline-md text-[20px] leading-7 text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary text-[24px]">database</span>
                  Data Management
                </h3>
              </div>
              <div className="flex flex-col gap-sm">
                <button 
                  onClick={() => console.log('Refreshing cache')}
                  className="w-full py-2.5 px-4 font-label-md text-label-md bg-surface border border-outline text-on-surface hover:bg-surface-container-low rounded-lg transition-all active:scale-95 flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-[20px]">cached</span>
                  Refresh Cache
                </button>
                <button 
                  onClick={() => console.log('Exporting audit log')}
                  className="w-full py-2.5 px-4 font-label-md text-label-md bg-surface border border-outline text-on-surface hover:bg-surface-container-low rounded-lg transition-all active:scale-95 flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-[20px]">download</span>
                  Export Audit Log
                </button>
              </div>
            </section>

          </div>
        </div>
        
        {/* Bottom spacing for mobile */}
        <div className="h-12 md:h-0"></div>
      </div>

      {/* Toast Notification */}
      {toast && toast.show && (
        <div className="fixed bottom-lg right-lg bg-surface-container-lowest border-l-4 border-primary shadow-lg rounded-r-lg p-4 flex items-center gap-3 z-50 animate-[slideIn_0.3s_cubic-bezier(0.16,1,0.3,1)_forwards]">
          <div className="w-8 h-8 rounded-full bg-primary-container/20 flex items-center justify-center text-primary shrink-0">
            <span className="material-symbols-outlined text-[20px]">check</span>
          </div>
          <div>
            <h4 className="font-label-md text-label-md text-on-surface">Settings Saved</h4>
            <p className="font-body-sm text-body-sm text-secondary mt-0.5">{toast.message}</p>
          </div>
          <button 
            className="ml-4 p-1 text-secondary hover:text-on-surface rounded focus:outline-none focus:ring-1 focus:ring-primary ml-auto"
            onClick={() => setToast(null)}
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
      )}
    </main>
  );
}
