import React, { useEffect, useState } from 'react';
import { GestureMapping, MappingConfig, getMappings, saveMappings, pressKey } from '../api/client';

const defaultMapping: GestureMapping = { gesture: '', action: '', action_type: 'key', hold_ms: 50 };

export default function KeyMappingsEditor() {
  const [config, setConfig] = useState<MappingConfig>({ mappings: [] });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      const data = await getMappings();
      setConfig(data);
      setLoading(false);
    })();
  }, []);

  const updateRow = (index: number, patch: Partial<GestureMapping>) => {
    setConfig((prev) => {
      const next = [...prev.mappings];
      next[index] = { ...next[index], ...patch } as GestureMapping;
      return { mappings: next };
    });
  };

  const addRow = () => setConfig((prev) => ({ mappings: [...prev.mappings, { ...defaultMapping }] }));

  const removeRow = (idx: number) =>
    setConfig((prev) => ({ mappings: prev.mappings.filter((_, i) => i !== idx) }));

  const handleSave = async () => {
    setSaving(true);
    await saveMappings(config);
    setSaving(false);
  };

  if (loading) return <div className="card">Loading mappings...</div>;

  return (
    <div className="card">
      <div className="flex" style={{ justifyContent: 'space-between', marginBottom: 8 }}>
        <div>
          <div className="small">Gesture → Key bindings</div>
          <div style={{ fontWeight: 600 }}>Customize macros</div>
        </div>
        <button onClick={addRow}>Add mapping</button>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Gesture</th>
            <th>Action</th>
            <th>Type</th>
            <th>Test</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {config.mappings.map((m, idx) => (
            <tr key={idx}>
              <td>
                <input
                  value={m.gesture}
                  onChange={(e) => updateRow(idx, { gesture: e.target.value })}
                  placeholder="open_hand"
                />
              </td>
              <td>
                <input
                  value={m.action}
                  onChange={(e) => updateRow(idx, { action: e.target.value })}
                  placeholder="space / ctrl+c / a,b,c"
                />
              </td>
              <td>
                <select
                  value={m.action_type}
                  onChange={(e) => updateRow(idx, { action_type: e.target.value as GestureMapping['action_type'] })}
                >
                  <option value="key">Key</option>
                  <option value="shortcut">Shortcut</option>
                  <option value="macro">Macro</option>
                </select>
              </td>
              <td>
                <button
                  className="secondary"
                  onClick={() => pressKey(config.mappings[idx])}
                  style={{ width: '100%' }}
                >
                  Try
                </button>
              </td>
              <td>
                <button className="secondary" onClick={() => removeRow(idx)}>
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex" style={{ marginTop: 12, justifyContent: 'space-between' }}>
        <button onClick={handleSave}>{saving ? 'Saving...' : 'Save mappings'}</button>
        <span className="small">Macros use commas, shortcuts use plus signs.</span>
      </div>
    </div>
  );
}
