import { useState } from 'react';
import { useComplaints } from '../hooks/useComplaints';
import { format } from 'date-fns';

export function ComplaintsPage() {
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
    selectedComplaintId,
    attemptSelectComplaint,
    selectedComplaint,
    loadingDetail,
    admins,
    internalNotes,
    handleNotesChange,
    hasUnsavedNotes,
    isSavingWorkflow,
    workflowError,
    workflowSuccess,
    handleSaveWorkflow,
    handleStatusChangeRequest,
    showUnsavedDialog,
    confirmSwitchComplaint,
    cancelSwitchComplaint,
    showCloseConfirmDialog,
    confirmStatusChange,
    cancelStatusChange
  } = useComplaints();

  const [showFilterPopover, setShowFilterPopover] = useState(false);

  const totalPages = Math.ceil(total / size) || 1;

  const renderPriority = (category: string) => {
    const isHigh = category?.toLowerCase().includes('hardware');
    const isMed = category?.toLowerCase().includes('billing');
    
    if (isHigh) {
      return <span className="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-sm font-bold bg-error-container text-on-error-container">High</span>;
    } else if (isMed) {
      return <span className="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-sm font-bold bg-tertiary-container text-on-tertiary-container">Med</span>;
    }
    return <span className="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-sm font-bold bg-surface-container text-on-surface">Low</span>;
  };

  const renderStatus = (status: string) => {
    switch (status) {
      case 'open':
        return <span className="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-sm font-bold bg-surface-container-high text-on-surface">Open</span>;
      case 'in_progress':
        return <span className="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-sm font-bold bg-secondary-container text-on-secondary-container">In-Progress</span>;
      case 'waiting':
        return <span className="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-sm font-bold bg-warning-container text-on-warning-container">Waiting</span>;
      case 'resolved':
        return <span className="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-sm font-bold bg-primary-container text-on-primary-container">Resolved</span>;
      default:
        return <span className="inline-flex items-center px-2.5 py-1 rounded-full font-label-sm text-label-sm font-bold bg-surface-container-high text-on-surface">{status}</span>;
    }
  };

  return (
    <main className="flex-1 p-lg md:p-xl overflow-y-auto max-w-7xl mx-auto w-full relative">
      
      {/* Modals */}
      {showUnsavedDialog && (
        <div className="fixed inset-0 bg-surface-dim/50 z-50 flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 max-w-sm w-full shadow-lg">
            <h3 className="font-headline-sm text-on-surface mb-2">Unsaved Changes</h3>
            <p className="font-body-sm text-on-surface-variant mb-6">You have unsaved changes in your Internal Notes. Do you want to save them before switching complaints?</p>
            <div className="flex justify-end gap-3">
              <button onClick={cancelSwitchComplaint} className="px-4 py-2 rounded-lg font-label-md text-on-surface hover:bg-surface-container transition-colors">Cancel</button>
              <button onClick={() => confirmSwitchComplaint(false)} className="px-4 py-2 rounded-lg font-label-md text-error hover:bg-error-container transition-colors">Discard</button>
              <button onClick={() => confirmSwitchComplaint(true)} className="px-4 py-2 rounded-lg font-label-md bg-primary text-on-primary hover:bg-primary-fixed-dim transition-colors">Save</button>
            </div>
          </div>
        </div>
      )}

      {showCloseConfirmDialog && (
        <div className="fixed inset-0 bg-surface-dim/50 z-50 flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 max-w-sm w-full shadow-lg">
            <h3 className="font-headline-sm text-on-surface mb-2">Confirm Resolution</h3>
            <p className="font-body-sm text-on-surface-variant mb-6">Are you sure you want to mark this complaint as Resolved? This action cannot be easily undone.</p>
            <div className="flex justify-end gap-3">
              <button onClick={cancelStatusChange} className="px-4 py-2 rounded-lg font-label-md text-on-surface hover:bg-surface-container transition-colors">Cancel</button>
              <button onClick={confirmStatusChange} className="px-4 py-2 rounded-lg font-label-md bg-primary text-on-primary hover:bg-primary-fixed-dim transition-colors">Confirm</button>
            </div>
          </div>
        </div>
      )}

      {/*  Page Header & Actions  */}
      <div className="flex items-center justify-between mb-6 flex-shrink-0">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="font-headline-lg text-headline-lg font-bold text-on-surface tracking-tight">Active Complaints</h2>
            {loadingList && <span className="material-symbols-outlined animate-spin text-secondary text-sm">progress_activity</span>}
          </div>
          <p className="font-body-sm text-body-sm text-secondary mt-1">Manage and resolve customer technical and billing issues.</p>
        </div>
        <div className="flex items-center gap-3 relative">
          
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-secondary text-[18px]">search</span>
            <input 
              type="text" 
              placeholder="Search Ticket ID..." 
              className="pl-9 pr-4 py-2 bg-surface border border-outline-variant rounded-lg font-body-sm text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-48 transition-all"
              value={filters.searchQuery}
              onChange={(e) => setFilters(f => ({ ...f, searchQuery: e.target.value }))}
            />
          </div>

          <button 
            onClick={() => setShowFilterPopover(!showFilterPopover)}
            className={`flex items-center gap-2 px-4 py-2 border rounded-lg font-label-md text-label-md transition-colors ${showFilterPopover ? 'bg-surface-container border-primary text-primary' : 'bg-surface border-outline-variant text-on-surface hover:bg-surface-container-low'}`}
          >
            <span className="material-symbols-outlined text-[18px]">filter_list</span>
            Filter
          </button>
          
          {showFilterPopover && (
            <div className="absolute top-12 right-0 bg-surface-container-lowest border border-outline-variant rounded-xl shadow-lg p-4 z-50 w-64 flex flex-col gap-4">
              <div>
                <label className="block font-label-sm text-secondary mb-1">Status</label>
                <select 
                  className="w-full bg-surface border border-outline-variant rounded-md py-1.5 px-3 font-body-sm focus:outline-none"
                  value={filters.status || ''}
                  onChange={(e) => setFilters(f => ({ ...f, status: e.target.value || undefined }))}
                >
                  <option value="">All Statuses</option>
                  <option value="open">Open</option>
                  <option value="in_progress">In-Progress</option>
                  <option value="waiting">Waiting</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
              <div>
                <label className="block font-label-sm text-secondary mb-1">Date Range</label>
                <select 
                  className="w-full bg-surface border border-outline-variant rounded-md py-1.5 px-3 font-body-sm focus:outline-none"
                  value={filters.dateRange || ''}
                  onChange={(e) => setFilters(f => ({ ...f, dateRange: e.target.value || undefined }))}
                >
                  <option value="">All Time</option>
                  <option value="30days">Last 30 Days</option>
                </select>
              </div>
              <button 
                onClick={() => { setFilters({ searchQuery: '' }); setShowFilterPopover(false); }}
                className="mt-2 w-full px-3 py-2 bg-surface-container text-on-surface rounded-md font-label-sm hover:bg-surface-container-high transition-colors"
              >
                Clear Filters
              </button>
            </div>
          )}

          <button className="flex items-center gap-2 px-4 py-2 bg-surface border border-outline-variant rounded-lg font-label-md text-label-md text-on-surface hover:bg-surface-container-low transition-colors">
            <span className="material-symbols-outlined text-[18px]">download</span>
            Export
          </button>
        </div>
      </div>

      {/*  Bento Grid Layout: Table (Left) + Detail Panel (Right)  */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-lg flex-1 min-h-[600px]">
        {/*  TABLE SECTION (Spans 2 columns)  */}
        <div className={`${selectedComplaintId ? 'xl:col-span-2' : 'xl:col-span-3'} bg-surface-container-lowest border border-outline-variant rounded-xl flex flex-col overflow-hidden shadow-sm transition-all duration-300`}>
          <div className="overflow-x-auto flex-1 relative">
            <table className="w-full text-left border-collapse whitespace-nowrap">
              <thead className="sticky top-0 bg-surface z-10 shadow-sm">
                <tr>
                  <th className="px-6 py-4 border-b border-outline-variant font-label-sm text-label-sm text-secondary font-medium tracking-wider">ID</th>
                  <th className="px-6 py-4 border-b border-outline-variant font-label-sm text-label-sm text-secondary font-medium tracking-wider">COMPLAINT SUBJECT</th>
                  <th className="px-6 py-4 border-b border-outline-variant font-label-sm text-label-sm text-secondary font-medium tracking-wider">CUSTOMER</th>
                  <th className="px-6 py-4 border-b border-outline-variant font-label-sm text-label-sm text-secondary font-medium tracking-wider">PRIORITY</th>
                  <th className="px-6 py-4 border-b border-outline-variant font-label-sm text-label-sm text-secondary font-medium tracking-wider">STATUS</th>
                  <th className="px-6 py-4 border-b border-outline-variant font-label-sm text-label-sm text-secondary font-medium tracking-wider">ASSIGNED TO</th>
                </tr>
              </thead>
              <tbody className="font-body-sm text-body-sm text-on-surface divide-y divide-outline-variant/50">
                
                {errorList && (
                  <tr><td colSpan={6} className="p-8 text-center text-error">{errorList}</td></tr>
                )}
                
                {!errorList && data.length === 0 && !loadingList && (
                  <tr><td colSpan={6} className="p-8 text-center text-secondary">No complaints found.</td></tr>
                )}

                {data.map((item) => (
                  <tr 
                    key={item.id} 
                    onClick={() => attemptSelectComplaint(item.id)}
                    className={`transition-colors cursor-pointer group ${selectedComplaintId === item.id ? 'bg-surface-container border-l-4 border-l-primary' : 'hover:bg-surface-container-low border-l-4 border-transparent'}`}
                  >
                    <td className={`px-6 py-4 font-label-md text-label-md font-semibold ${selectedComplaintId === item.id ? 'text-primary' : ''}`}>
                      {item.ticket_id}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium">{item.category}</div>
                      <div className="text-secondary text-[13px] mt-0.5 max-w-[200px] truncate">{item.description}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center font-bold text-xs">
                          {item.phone_number ? item.phone_number.substring(item.phone_number.length - 2) : 'XX'}
                        </div>
                        <div>
                          <div className="font-medium">User: {item.phone_number || 'N/A'}</div>
                          <div className="text-secondary text-[12px]">{format(new Date(item.created_at), 'MMM dd')}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {renderPriority(item.category)}
                    </td>
                    <td className="px-6 py-4">
                      {renderStatus(item.workflow?.internal_status || 'open')}
                    </td>
                    <td className="px-6 py-4">
                      {item.workflow?.assigned_admin_name ? (
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-bold text-[10px]">
                            {item.workflow.assigned_admin_name.substring(0, 2).toUpperCase()}
                          </div>
                          <span className="text-secondary">{item.workflow.assigned_admin_name}</span>
                        </div>
                      ) : (
                        <span className="text-secondary italic">Unassigned</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/*  Pagination Footer  */}
          <div className="border-t border-outline-variant p-4 flex items-center justify-between bg-surface-bright mt-auto">
            <p className="font-body-sm text-body-sm text-secondary">
              Showing {Math.min((page - 1) * size + 1, total)}-{Math.min(page * size, total)} of {total} complaints
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

        {/*  DETAIL PANEL SECTION (Spans 1 column)  */}
        {selectedComplaintId && (
          <div className="xl:col-span-1 bg-surface-container-lowest border border-outline-variant rounded-xl flex flex-col overflow-hidden shadow-md relative">
            
            {loadingDetail && !selectedComplaint && (
              <div className="absolute inset-0 bg-surface/50 z-10 flex items-center justify-center">
                <span className="material-symbols-outlined animate-spin text-primary text-3xl">progress_activity</span>
              </div>
            )}

            {/*  Detail Header  */}
            <div className="p-5 border-b border-outline-variant flex items-start justify-between bg-surface-bright">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-headline-md text-[20px] leading-tight font-bold text-on-surface">
                    {selectedComplaint?.ticket_id || 'Loading...'}
                  </h3>
                  {selectedComplaint && renderPriority(selectedComplaint.category)}
                </div>
                <p className="font-body-sm text-body-sm text-secondary">
                  {selectedComplaint ? `Created ${format(new Date(selectedComplaint.created_at), 'MMM dd, yyyy HH:mm')}` : ''}
                </p>
              </div>
              <button 
                onClick={() => attemptSelectComplaint(null)}
                className="text-secondary hover:text-on-surface p-1 rounded-md hover:bg-surface-container transition-colors"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            
            {selectedComplaint && (
              <div className="flex-1 overflow-y-auto p-5 space-y-6">
                {/*  Customer Context  */}
                <div className="p-4 bg-surface rounded-lg border border-outline-variant/50">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center font-bold text-lg">
                      {selectedComplaint.phone_number ? selectedComplaint.phone_number.substring(selectedComplaint.phone_number.length - 2) : 'XX'}
                    </div>
                    <div>
                      <div className="font-label-md text-label-md font-semibold text-on-surface">User ID: {selectedComplaint.phone_number || 'N/A'}</div>
                      <div className="font-body-sm text-body-sm text-secondary flex items-center gap-1 mt-0.5">
                        <span className="material-symbols-outlined text-[14px]">call</span> {selectedComplaint.phone_number || 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>

                {/*  Description  */}
                <div>
                  <h4 className="font-label-md text-label-md font-semibold text-on-surface mb-2">{selectedComplaint.category}</h4>
                  <div className="bg-surface-container-low p-4 rounded-lg font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                    "{selectedComplaint.description}"
                  </div>
                </div>

                {/*  Workflow Controls  */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block font-label-sm text-label-sm text-secondary mb-1.5">Status</label>
                    <div className="relative">
                      <select 
                        disabled={isSavingWorkflow}
                        value={selectedComplaint.workflow?.internal_status || 'open'}
                        onChange={(e) => handleStatusChangeRequest(e.target.value)}
                        className="w-full appearance-none bg-surface border border-outline-variant rounded-md py-2 pl-3 pr-8 font-body-sm text-body-sm text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none disabled:opacity-50"
                      >
                        <option value="open">Open</option>
                        <option value="in_progress">In-Progress</option>
                        <option value="waiting">Waiting on Customer</option>
                        <option value="resolved">Resolved</option>
                      </select>
                      <span className="material-symbols-outlined absolute right-2 top-1/2 -translate-y-1/2 text-secondary pointer-events-none text-[20px]">arrow_drop_down</span>
                    </div>
                  </div>
                  <div>
                    <label className="block font-label-sm text-label-sm text-secondary mb-1.5">Assignee</label>
                    <div className="relative">
                      <select 
                        disabled={isSavingWorkflow}
                        value={selectedComplaint.workflow?.assigned_admin_id || 'unassigned'}
                        onChange={(e) => handleSaveWorkflow({ assigned_admin_id: e.target.value === 'unassigned' ? null : e.target.value })}
                        className="w-full appearance-none bg-surface border border-outline-variant rounded-md py-2 pl-3 pr-8 font-body-sm text-body-sm text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none disabled:opacity-50"
                      >
                        <option value="unassigned">Unassigned</option>
                        {admins.map((admin) => (
                          <option key={admin.id} value={admin.id}>{admin.full_name}</option>
                        ))}
                      </select>
                      <span className="material-symbols-outlined absolute right-2 top-1/2 -translate-y-1/2 text-secondary pointer-events-none text-[20px]">arrow_drop_down</span>
                    </div>
                  </div>
                </div>

                {/*  Internal Notes  */}
                <div>
                  <label className="block font-label-sm text-label-sm text-secondary mb-1.5 flex justify-between items-end">
                    Internal Notes (Private)
                    {workflowSuccess && <span className="text-primary text-[11px] font-bold">Saved!</span>}
                    {workflowError && <span className="text-error text-[11px] font-bold">{workflowError}</span>}
                  </label>
                  <textarea 
                    disabled={isSavingWorkflow}
                    value={internalNotes}
                    onChange={(e) => handleNotesChange(e.target.value)}
                    className="w-full bg-surface border border-outline-variant rounded-md p-3 font-body-sm text-body-sm text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none disabled:opacity-50" 
                    placeholder="Add an update or note..." 
                    rows={4}
                  ></textarea>
                  <div className="flex justify-end mt-2">
                    <button 
                      disabled={!hasUnsavedNotes || isSavingWorkflow}
                      onClick={() => handleSaveWorkflow({ internal_notes: internalNotes })}
                      className="px-4 py-2 bg-primary text-on-primary rounded-md font-label-md text-label-md font-medium hover:bg-primary-container hover:text-on-primary-container transition-colors shadow-sm disabled:opacity-50 disabled:bg-surface-container disabled:text-on-surface"
                    >
                      {isSavingWorkflow ? 'Saving...' : 'Save Note'}
                    </button>
                  </div>
                </div>

                {/*  Timeline  */}
                <div>
                  <h4 className="font-label-sm text-label-sm font-semibold text-secondary mb-4 uppercase tracking-wider">Activity Timeline</h4>
                  <div className="bg-surface-container-low border border-outline-variant border-dashed rounded-lg p-6 flex flex-col items-center justify-center text-center">
                    <span className="material-symbols-outlined text-secondary text-4xl mb-2">history</span>
                    <p className="font-label-md text-on-surface">Timeline Coming Soon</p>
                    <p className="font-body-sm text-secondary mt-1">Audit logs will be displayed here in a future update.</p>
                  </div>
                </div>

              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
