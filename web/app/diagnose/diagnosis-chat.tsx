'use client';

import { useEffect, useRef } from 'react';
import { ArrowUp, LoaderCircle, Paperclip, Send, Stethoscope, Upload, User, Wrench, Smartphone, X, Zap } from 'lucide-react';
import type { DiagnosisResult } from './page';
import { AssistantResponse } from './chat-response';
import './chat.css';

export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  question_id?: string | null;
  image?: string | null;
  assessment?: DiagnosisResult;
};

export function ChatTranscript({ messages, loading, onAnswer, onDraft }: { messages: ChatMessage[]; loading: boolean; onAnswer: (message: string) => void; onDraft: (message: string) => void }) {
  const lastAssistantIndex = messages.findLastIndex(message => message.role === 'assistant');
  const latest = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (messages.length) latest.current?.scrollIntoView({ block: 'start', behavior: 'instant' });
  }, [messages.length]);

  return (
    <section aria-label="Diagnosis conversation" className="diagnosis-transcript">
      {messages.length === 0 && (
        <div className="chat-welcome">
          <span className="diagnosis-intro-badge"><Zap size={13} aria-hidden="true" /> AI fault detection &amp; recovery</span>
          <h1>Diagnose. Repair. <span>Replace.</span></h1>
          <p>Describe your phone issue or upload a photo. Get a diagnosis, repair guidance, and replacement options.</p>
          <div className="chat-examples" role="group" aria-label="Example phone issues">
            {['A line on my screen', 'Battery drains quickly', 'Phone will not charge'].map(example => <button key={example} type="button" onClick={() => onDraft(example)}>{example}</button>)}
          </div>
        </div>
      )}
      <div role="log" aria-label="Messages" aria-live="polite" aria-relevant="additions" aria-busy={loading}>
        {messages.map((message, index) => {
          const previous = messages.slice(0, index).findLast(item => item.role === 'assistant' && item.assessment)?.assessment;
          const request = messages[index - 1]?.role === 'user' ? messages[index - 1].content : '';
          const wantsSteps = /\b(?:steps?|fix|troubleshoot|diy|manuals?|guides?|videos?|tutorials?|images?|photos?|pictures?)\b|\bhow\b.{0,30}\brepair\b|\bwhat\b.{0,20}\bdo\b/i.test(request);
          const focusedQuestion = /\b(?:cost|price|quote|how much|recommend|upgrade|replace|thanks|thank you)\b/i.test(request);
          const showSteps = Boolean(message.assessment?.troubleshooting?.escalate_to_technician || wantsSteps || (!focusedQuestion && previous?.diagnosis.fault_category !== message.assessment?.diagnosis.fault_category));
          return (
          <div key={message.id} ref={index === messages.length - 1 ? latest : undefined} className={`chat-message chat-message-${message.role}`}>
            <span className="chat-avatar" aria-hidden="true">{message.role === 'user' ? <User size={18} /> : <Stethoscope size={18} />}</span>
            <article className="chat-message-body" aria-label={`${message.role === 'user' ? 'You' : 'REVIVAI'} message`}>
              <p className="chat-message-author">{message.role === 'user' ? 'You' : 'REVIVAI'}</p>
              {message.image && <img src={message.image} alt="Your uploaded phone issue" className="chat-upload" />}
              {message.role === 'assistant' ? (
                <AssistantResponse content={message.content} questionId={message.question_id} result={message.assessment} showSteps={showSteps} active={!loading && index === lastAssistantIndex && index === messages.length - 1} onAnswer={onAnswer} />
              ) : <p className="chat-user-text">{message.content}</p>}
            </article>
          </div>
          );
        })}
      </div>
      {loading && <p role="status" className="chat-thinking"><span className="chat-thinking-dots" aria-hidden="true"><i /><i /><i /></span>Thinking through your phone issue…</p>}
    </section>
  );
}

type ComposerProps = {
  intro?: boolean;
  value: string;
  onChange: (value: string) => void;
  onSubmit: (event: React.FormEvent) => void;
  image: string | null;
  onUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onRemoveImage: () => void;
  loading: boolean;
  confirming: boolean;
  hasResult: boolean;
  view: string;
  onChooseOption: (view: 'repair' | 'recommendations') => void;
  error: string;
};

export function ChatComposer(props: ComposerProps) {
  const dock = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    const textarea = input.current;
    if (!textarea) return;
    textarea.style.height = 'auto';
    const maximumHeight = props.intro ? 240 : 120;
    const minimumHeight = props.intro ? 160 : 44;
    textarea.style.height = `${Math.min(maximumHeight, Math.max(minimumHeight, textarea.scrollHeight))}px`;
    textarea.style.overflowY = textarea.scrollHeight > maximumHeight ? 'auto' : 'hidden';
  }, [props.value, props.intro]);
  useEffect(() => {
    if (props.hasResult && !props.loading && !props.confirming && window.matchMedia('(pointer: fine)').matches) {
      input.current?.focus({ preventScroll: true });
    }
  }, [props.hasResult, props.loading, props.confirming]);
  useEffect(() => {
    if (!dock.current) return;
    const observer = new ResizeObserver(([entry]) => {
      document.documentElement.style.setProperty('--diagnosis-dock-height', `${entry.target.getBoundingClientRect().height + 32}px`);
    });
    observer.observe(dock.current);
    return () => {
      observer.disconnect();
      document.documentElement.style.removeProperty('--diagnosis-dock-height');
    };
  }, []);
  const disabled = props.loading || props.confirming;
  return (
    <div ref={dock} className={`diagnosis-dock${props.intro ? ' diagnosis-intro-form' : ''}`}>
      {props.error && <p role="alert" className="mb-2 text-sm text-rose-ink-300">{props.error} Your message is kept so you can try again.</p>}
      <form onSubmit={props.onSubmit} aria-label="Send a message to REVIVAI">
        {props.image && <div className="relative mb-2 w-fit"><img src={props.image} alt="Photo ready to send" className="h-14 w-14 rounded-lg object-cover" /><button type="button" onClick={props.onRemoveImage} disabled={disabled} aria-label="Remove attached photo" className="absolute -top-1 -right-1 rounded-full bg-raised p-1 text-foreground"><X size={12} /></button></div>}
        <label htmlFor="diagnosis-message" className={props.intro ? 'diagnosis-intro-label' : 'sr-only'}>{props.intro ? <><Smartphone size={14} aria-hidden="true" /> State your phone issue or symptoms</> : 'Message REVIVAI'}</label>
        <div className="chat-input-row">
          <textarea
            ref={input}
            id="diagnosis-message"
            value={props.value}
            onChange={event => props.onChange(event.target.value)}
            maxLength={2000}
            rows={props.intro ? 5 : 1}
            aria-describedby="chat-composer-help"
            disabled={disabled}
            placeholder={props.intro ? 'e.g., My phone screen cracked after a fall, or the display shows green lines…' : props.confirming ? 'Confirm your phone above to continue…' : props.hasResult ? 'Message REVIVAI…' : 'Describe your phone issue…'}
            onKeyDown={event => {
              if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
                event.preventDefault();
                if (!disabled && (props.value.trim() || props.image)) event.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <div className={props.intro ? 'diagnosis-intro-actions' : 'flex items-center gap-1.5'}>
            <label className={`chat-attach ${disabled ? 'opacity-40' : ''}`} title="Attach a phone photo">
              {props.intro ? <Upload size={16} aria-hidden="true" /> : <Paperclip size={18} aria-hidden="true" />}
              <span className={props.intro ? undefined : 'sr-only'}>{props.intro ? 'Upload Fault Image' : 'Attach a phone photo'}</span>
              <input type="file" accept="image/*" className="sr-only" disabled={disabled} onChange={props.onUpload} />
            </label>
            <button type="submit" disabled={disabled || (!props.value.trim() && !props.image)} className="chat-send" aria-label="Send message">{props.loading ? <LoaderCircle className="size-4 animate-spin motion-reduce:animate-none" aria-hidden="true" /> : props.intro ? <>Run AI Diagnosis <Send size={15} aria-hidden="true" /></> : <ArrowUp size={21} aria-hidden="true" />}</button>
          </div>
        </div>
      </form>
      <div id="chat-composer-help" className="chat-composer-help">
        <span>{props.confirming ? 'Confirm your phone above to continue.' : !props.hasResult ? 'Confirm your phone after sending your issue.' : 'Add a detail or ask a question.'}</span>
        <span className="chat-keyboard-hint">Enter to send · Shift + Enter for a new line</span>
      </div>
      <div role="group" aria-label="Repair and replacement options" className="chat-options">
        <button type="button" disabled={!props.hasResult || props.loading} onClick={() => props.onChooseOption('repair')} aria-pressed={props.view === 'repair'}>
          <Wrench size={18} aria-hidden="true" />
          <span><span className="chat-option-label">Option A</span><span className="chat-option-title">Check Repair Cost</span></span>
        </button>
        <button type="button" disabled={!props.hasResult || props.loading} onClick={() => props.onChooseOption('recommendations')} aria-pressed={props.view === 'recommendations'}>
          <Smartphone size={18} aria-hidden="true" />
          <span><span className="chat-option-label">Option B</span><span className="chat-option-title">Explore Recommended Upgrades</span></span>
        </button>
      </div>
    </div>
  );
}
