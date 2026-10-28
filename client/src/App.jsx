import { useState } from 'react';

const TONES = ['professional', 'playful', 'luxury', 'casual'];

export default function App() {
  const [form, setForm] = useState({ name: '', category: '', features: '', keywords: '', tone: 'professional' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function generate(e) {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Something went wrong');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function copy() {
    const text = `${result.title}\n\n${result.description}\n\n${result.bullets.map((b) => `- ${b}`).join('\n')}`;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <main>
      <h1>AI Product Description Generator</h1>
      <p className="sub">Turn a few product details into SEO-friendly fashion copy.</p>

      <form onSubmit={generate}>
        <label>Product name *<input value={form.name} onChange={set('name')} placeholder="Linen Co-ord Set" required /></label>
        <label>Category<input value={form.category} onChange={set('category')} placeholder="Women's Western Wear" /></label>
        <label>Key features (one per line or comma separated)
          <textarea rows="4" value={form.features} onChange={set('features')} placeholder={'100% linen\nRelaxed fit\nMachine washable'} />
        </label>
        <label>SEO keywords<input value={form.keywords} onChange={set('keywords')} placeholder="linen set, summer outfit" /></label>
        <label>Tone
          <select value={form.tone} onChange={set('tone')}>
            {TONES.map((t) => <option key={t}>{t}</option>)}
          </select>
        </label>
        <button disabled={loading}>{loading ? 'Generating…' : 'Generate description'}</button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <section className="result">
          <h2>{result.title}</h2>
          <p>{result.description}</p>
          <ul>{result.bullets.map((b, i) => <li key={i}>{b}</li>)}</ul>
          <div className="row">
            <button onClick={copy}>{copied ? 'Copied!' : 'Copy'}</button>
            <small>Generated in {(result.elapsed_ms / 1000).toFixed(1)}s</small>
          </div>
        </section>
      )}
    </main>
  );
}
