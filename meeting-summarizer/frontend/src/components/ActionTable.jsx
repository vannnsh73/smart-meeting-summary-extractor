import React, { useState } from 'react';

function ActionTable({ items }) {
  const [sortConfig, setSortConfig] = useState(null);

  if (!items || items.length === 0) {
    return <p className="body-md text-muted">No action items found.</p>;
  }

  const sortedItems = [...items].sort((a, b) => {
    if (!sortConfig) return 0;
    
    if (sortConfig.key === 'priority') {
      const priorityWeights = { 'high': 3, 'medium': 2, 'low': 1 };
      const valA = priorityWeights[a.priority?.toLowerCase()] || 0;
      const valB = priorityWeights[b.priority?.toLowerCase()] || 0;
      return sortConfig.direction === 'asc' ? valA - valB : valB - valA;
    }
    
    // Sort strings
    if (a[sortConfig.key] < b[sortConfig.key]) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }
    if (a[sortConfig.key] > b[sortConfig.key]) {
      return sortConfig.direction === 'asc' ? 1 : -1;
    }
    return 0;
  });

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getPriorityBadgeClass = (priority) => {
    const p = (priority || '').toLowerCase();
    if (p === 'high') return 'badge badge-high';
    if (p === 'medium') return 'badge badge-medium';
    if (p === 'low') return 'badge badge-low';
    return 'badge';
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="action-table">
        <thead>
          <tr>
            <th onClick={() => requestSort('task')}>Task ↕</th>
            <th onClick={() => requestSort('owner')}>Owner ↕</th>
            <th onClick={() => requestSort('deadline')}>Deadline ↕</th>
            <th onClick={() => requestSort('priority')}>Priority ↕</th>
          </tr>
        </thead>
        <tbody className="body-md">
          {sortedItems.map((item, index) => (
            <tr key={index}>
              <td>{item.task}</td>
              <td>{item.owner}</td>
              <td>{item.deadline}</td>
              <td>
                <span className={getPriorityBadgeClass(item.priority)}>
                  {item.priority || 'Unknown'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ActionTable;
