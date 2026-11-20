'use client';

import { useEffect, useRef, useState } from 'react';
import { AlertTriangle, BookOpen, Check, Copy, ExternalLink } from 'lucide-react';
import type { DiagnosisResult } from './page';
import { RepairMediaGuide } from './repair-media';

const quickAnswers: Record<string, { label: string; message: string }[]> = {
  screen_restart: [
    { label: 'Yes, it stays', message: 'Yes, the line stays visible after restarting.' },
    { label: 'No, it disappears', message: 'No, the line disappears after restarting.' },
  ],
  screen_drop: [
    { label: 'Yes', message: 'Yes, the line started after the phone was dropped.' },
    { label: 'No', message: 'No, the phone was not dropped.' },
  ],
  screen_liquid: [
    { label: 'Yes', message: 'Yes, the phone was exposed to liquid.' },
    { label: 'No', message: 'No, the phone has not been exposed to liquid.' },
  ],
  screen_pattern: [
    { label: 'Always visible', message: 'The line is always visible.' },
    { label: 'Comes and goes', message: 'The line comes and goes.' },
  ],
  charging_cable: [
    { label: 'Yes, already tried', message: 'Yes, I have already tried a known-good compatible cable and power adapter.' },
    { label: 'Not yet', message: 'I have not tried another cable or power adapter yet.' },
  ],
  battery_when: [
    { label: 'While idle', message: 'The battery drains while the phone is idle.' },
    { label: 'During use', message: 'The battery drains mainly while I use the phone.' },
  ],
  overheating_when: [
    { label: 'While charging', message: 'The phone gets hot while charging.' },
    { label: 'During heavy use', message: 'The phone gets hot during heavy use.' },
    { label: 'Even when idle', message: 'The phone gets hot even when idle.' },
  ],
  performance_when: [
    { label: 'One app', message: 'The problem happens in one app.' },
    { label: 'The whole phone', message: 'The problem happens across the whole phone.' },
  ],
};

type Source = { url: string; title: string };

function collectSources(result: DiagnosisResult) {
  const sources = new Map<string, Source>();
  for (const step of result.troubleshooting?.detailed_steps ?? []) {
    for (const resource of step.resources ?? []) {
      if (!sources.has(resource.url)) sources.set(resource.url, { url: resource.url, title: resource.title });
    }
  }
  for (const spec of result.spec_answers ?? []) {
    if (!spec.source_url) continue;
    const source = sources.get(spec.source_url) ?? { url: spec.source_url, title: spec.source || 'Device specifications' };
    sources.set(spec.source_url, source);
  }
  if (result.repair_cost?.source_url && !sources.has(result.repair_cost.source_url)) {
    sources.set(result.repair_cost.source_url, { url: result.repair_cost.source_url, title: result.repair_cost.source || 'Repair estimate source' });
  }
  return [...sources.values()];
}

function domain(url: string) {
  try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return 'Source reference'; }
}

export function AssistantResponse({ content, questionId, result, active, showSteps = true, onAnswer }: {
  content: string;
  questionId?: string | null;
  result?: DiagnosisResult;
  active: boolean;
  showSteps?: boolean;
  onAnswer: (message: string) => void;
}) {
  const steps = showSteps ? (result?.troubleshooting?.steps ?? []).filter(step => !/^Hardware context:/i.test(step)) : [];
  // Present a guide sentence once when it was also included verbatim in the reply.
  const prose = steps.reduce((text, step) => {
    const escaped = step.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return text.replace(new RegExp(`(^|[.!?]\\s+|\\n+)${escaped}(?=\\s|$)`, 'g'), '$1');
  }, content);
  const paragraphs = prose.trim().split(/\n\s*\n/).map(paragraph => paragraph.trim()).filter(Boolean);
  const last = paragraphs.at(-1);
  const question = last && /\?\s*$/.test(last) && last.length < 360 ? paragraphs.pop() : null;
  const answers = questionId ? quickAnswers[questionId] ?? [] : [];
  const sources = result ? collectSources(result) : [];
  const safety = (result?.safety_flags ?? []).length > 0;
  const copyText = [paragraphs.join('\n\n'), steps.length ? steps.map((step, index) => `${index + 1}. ${step}`).join('\n') : '', question,
    sources.length ? `Resources:\n${sources.map(source => `${source.title}: ${source.url}`).join('\n')}` : ''].filter(Boolean).join('\n\n');

  return (
    <>
      {paragraphs.length > 0 && <section className="chat-answer-section" aria-label="Assessment"><h3 className="chat-answer-section-title">What this means</h3><div className="chat-prose">{paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}</div></section>}
      {steps.length > 0 && (
        <div className="chat-repair-guidance">
          {result ? <RepairMediaGuide steps={steps} result={result} /> : <><p className="chat-guidance-intro">{safety ? 'Please take these safety steps:' : 'Here’s what you can do next:'}</p><ol className="chat-repair-steps">{steps.map((step, index) => <li key={index}>{step}</li>)}</ol></>}
        </div>
      )}
      {result && (result.safety_flags ?? []).length > 0 && (
        <aside className="chat-safety" aria-label="Safety guidance">
          <p className="chat-safety-title"><AlertTriangle size={17} aria-hidden="true" /> Safety first</p>
          {result.safety_flags.map(flag => <p key={flag.code}>{flag.message}</p>)}
        </aside>
      )}
      {question && (
        <section aria-label="Follow-up question" className={`chat-question ${active ? 'chat-question-active' : ''}`}>
          <h3 className="chat-answer-section-title">One quick question</h3>
          <p className="chat-question-text">{question}</p>
          {active && answers.length > 0 && (
            <div className="chat-quick-answers" role="group" aria-label="Quick answers">
              {answers.map(answer => <button key={answer.label} type="button" onClick={() => onAnswer(answer.message)}>{answer.label}</button>)}
            </div>
          )}
        </section>
      )}
      {result?.diagnosis.image_attached && !result.diagnosis.image_reviewed && <p className="chat-photo-note">This assessment uses your description. Automated analysis of the attached photo was not available.</p>}
      <footer className="chat-answer-resources" aria-label="Resources for this answer">
        <h3 className="chat-answer-section-title">Resources &amp; further reading</h3>
        {sources.length > 0 ? (
          <ul className="chat-resource-links">
            {sources.map(source => <li key={source.url}><a href={source.url} target="_blank" rel="noopener noreferrer"><BookOpen size={15} aria-hidden="true" /><span><span className="chat-resource-title">{source.title}</span><span className="chat-resource-domain">{domain(source.url)}</span></span><ExternalLink size={13} className="chat-resource-external" aria-hidden="true" /></a></li>)}
          </ul>
        ) : <p className="chat-resources-empty">No linked resources are available for this answer.</p>}
      </footer>
      <CopyResponse text={copyText} />
    </>
  );
}

function CopyResponse({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const [failed, setFailed] = useState(false);
  const resetTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => { if (resetTimer.current) clearTimeout(resetTimer.current); }, []);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setFailed(false);
      if (resetTimer.current) clearTimeout(resetTimer.current);
      resetTimer.current = setTimeout(() => setCopied(false), 2000);
    } catch { setFailed(true); }
  }

  return <div className="chat-answer-actions"><button type="button" onClick={copy} aria-label={copied ? 'Response copied' : 'Copy response'} title="Copy response">{copied ? <Check size={15} aria-hidden="true" /> : <Copy size={15} aria-hidden="true" />}<span>{copied ? 'Copied' : 'Copy'}</span></button><span role="status">{failed ? 'Could not copy. Select the reply text to copy it.' : copied ? 'Response copied.' : ''}</span></div>;
}
