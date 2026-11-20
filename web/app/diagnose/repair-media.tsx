'use client';

import { useEffect, useId, useRef, useState } from 'react';
import { Check, ExternalLink, ImageIcon, Play, X } from 'lucide-react';
import videos from '@/data/repair-videos.json';
import imageData from '@/data/repair-images.json';
import type { DiagnosisResult } from './page';

type StepKind = 'backup' | 'restart' | 'protect' | 'service' | 'charging' | 'port' | 'power' | 'charging-care' | 'settings' | 'cooldown' | 'safety' | 'observe';
type ReferenceImage = { id: string; brand: string; models?: string[]; stepKind: string; instructionPattern: string; src: string; alt: string; source: string; sourceUrl: string; caption: string; fit: string };
const imageCatalog: ReferenceImage[] = imageData;

function actionIsProhibited(instruction: string) {
  return /\b(?:do not|don't|avoid|never)\s+(?:\w+\s+){0,3}(?:restart|reboot|back\s?up|charg(?:e|ing)|connect|plug|inspect|look)\b/i.test(instruction);
}

export function referenceImage(kind: StepKind, brand: string, model: string, instruction: string) {
  if (actionIsProhibited(instruction)) return undefined;
  const matches = (image: ReferenceImage) => image.stepKind === kind
    && (!image.models || image.models.includes(model))
    && new RegExp(image.instructionPattern, 'i').test(instruction);
  return imageCatalog.find(image => image.brand === brand && matches(image))
    ?? imageCatalog.find(image => image.brand === 'any' && matches(image));
}

const stepLabels: Record<StepKind, { title: string }> = {
  backup: { title: 'Back up your data' },
  restart: { title: 'Restart the phone and check again' },
  protect: { title: 'Protect the screen' },
  service: { title: 'Arrange a professional inspection' },
  charging: { title: 'Check the cable and adapter' },
  port: { title: 'Inspect the charging port' },
  power: { title: 'Try a different power source' },
  'charging-care': { title: 'Review your charging habits' },
  settings: { title: 'Check your settings' },
  cooldown: { title: 'Let the phone cool' },
  safety: { title: 'Put safety first' },
  observe: { title: 'Note what happens' },
};

export function stepKind(text: string, escalated = false): StepKind {
  if (escalated && /stop|do not|unplug|switch.*off|flammable|move away/i.test(text)) return 'safety';
  if (/back\s?up/i.test(text)) return 'backup';
  if (/qualified|repairer|technician|inspection|diagnostic check/i.test(text)) return 'service';
  if (/do not.*(?:press|heat|open)|avoid pressing|cover the cracks/i.test(text)) return 'protect';
  if (/cool|shaded|fridge|freezer/i.test(text)) return 'cooldown';
  if (/\bport\b/i.test(text) && /look|inspect|lint|debris/i.test(text)) return 'port';
  if (/different.*(?:socket|power)|wall socket|power source/i.test(text)) return 'power';
  if (/avoid|do not|never/i.test(text) && /charg/i.test(text)) return 'charging-care';
  if (/restart/i.test(text)) return 'restart';
  if (/cable|adapter|socket|charger|port/i.test(text)) return 'charging';
  if (/settings|apps|updates|storage|caches/i.test(text)) return 'settings';
  return 'observe';
}

export function RepairMediaGuide({ steps, result }: { steps: string[]; result: DiagnosisResult }) {
  const [completed, setCompleted] = useState<Set<number>>(new Set());
  const [selected, setSelected] = useState<number | null>(null);
  const [failedImages, setFailedImages] = useState<Set<number>>(new Set());
  const dialog = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  const escalated = Boolean(result.troubleshooting?.escalate_to_technician || result.safety_flags?.length);
  const kinds = steps.map(step => stepKind(step, escalated));
  const brand = result.matched_device?.brand;
  const model = result.matched_device?.model;
  const references = kinds.map((kind, index) => escalated || failedImages.has(index) ? undefined : referenceImage(kind, brand || '', model || '', steps[index]));
  const matches = escalated ? [] : videos.filter(video => video.brand === brand && steps.some((step, index) => kinds[index] === video.stepKind && !actionIsProhibited(step)))
    .sort((first, second) => kinds.indexOf(first.stepKind as StepKind) - kinds.indexOf(second.stepKind as StepKind));

  useEffect(() => {
    if (selected !== null && !dialog.current?.open) dialog.current?.showModal();
  }, [selected]);

  return (
    <section className="repair-visual-guide" aria-label="Step-by-step guidance with images and videos">
      <div className="repair-guide-heading"><div><p className="repair-guide-eyebrow">{escalated ? 'Safety checklist' : 'Step-by-step guidance'}</p><h3>{escalated ? 'Keep yourself and your phone safe' : 'Read, see and watch each step'}</h3></div><span className="repair-progress" role="status">{completed.size} of {steps.length} completed</span></div>
      <ol className="repair-step-grid">
        {steps.map((step, index) => {
          const art = stepLabels[kinds[index]];
          const professional = kinds[index] === 'service';
          const image = references[index];
          const stepVideos = actionIsProhibited(step) ? [] : matches.filter(video => video.stepKind === kinds[index]);
          return (
            <li key={index} className={`repair-step-card ${completed.has(index) ? 'repair-step-complete' : ''}`}>
              {image && <button type="button" className="repair-step-visual" data-image-type="reference" onClick={() => setSelected(index)} aria-label={`Enlarge image for step ${index + 1}: ${art.title}`}>
                <img src={image.src} alt={image.alt} style={{ objectFit: image.fit === 'contain' ? 'contain' : 'cover' }} loading="lazy" width={640} height={360} onError={() => setFailedImages(previous => new Set(previous).add(index))} />
                <span className="repair-step-index">Step {index + 1}</span><span className="repair-enlarge"><ImageIcon size={14} aria-hidden="true" /> Enlarge</span>
              </button>}
              <div className="repair-step-copy">
                {!image && <span className="repair-text-step-index">Step {index + 1}</span>}
                <div className="repair-step-title"><h4>{art.title}</h4>{professional && <span>Professional</span>}</div>
                <p>{step}</p>
                {image && <div className="repair-image-credit"><a href={image.sourceUrl} target="_blank" rel="noopener noreferrer">Image: {image.source} <ExternalLink size={11} aria-hidden="true" /></a><span>{image.caption}</span></div>}
                {stepVideos.length > 0 && <div className="repair-step-video"><p>Watch this step</p>{stepVideos.map(video => <VideoPreview key={video.id} video={video} />)}</div>}
                <label className="repair-step-check"><input type="checkbox" aria-label={`Mark step ${index + 1}: ${art.title} as complete`} checked={completed.has(index)} onChange={() => setCompleted(previous => { const next = new Set(previous); if (next.has(index)) next.delete(index); else next.add(index); return next; })} /><span>{completed.has(index) ? 'Completed' : 'Mark as complete'}</span>{completed.has(index) && <Check size={14} aria-hidden="true" />}</label>
              </div>
            </li>
          );
        })}
      </ol>
      {references.some(Boolean) && <p className="repair-illustration-note">Photos illustrate the step; manufacturer images show controls. Pictured devices and screen layouts may differ.</p>}
      <dialog ref={dialog} className="repair-image-dialog" aria-labelledby={titleId} onClose={() => setSelected(null)} onClick={event => { if (event.target === event.currentTarget) dialog.current?.close(); }}>
        <button type="button" className="repair-dialog-close" onClick={() => dialog.current?.close()} aria-label="Close image"><X size={20} aria-hidden="true" /></button>
        {selected !== null && references[selected] && <><img src={references[selected]!.src} alt={references[selected]!.alt} width={640} height={360} /><div><h3 id={titleId}>Step {selected + 1}: {stepLabels[kinds[selected]].title}</h3><p>{steps[selected]}</p><a className="repair-dialog-source" href={references[selected]!.sourceUrl} target="_blank" rel="noopener noreferrer">Image source: {references[selected]!.source}</a></div></>}
      </dialog>
    </section>
  );
}

function VideoPreview({ video }: { video: (typeof videos)[number] }) {
  const [playing, setPlaying] = useState(false);
  const [thumbnailFailed, setThumbnailFailed] = useState(false);
  return (
    <article className="repair-video-card">
      <div className="repair-video-player">
        {playing ? <iframe src={`https://www.youtube-nocookie.com/embed/${video.id}?autoplay=1&rel=0`} title={video.title} allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowFullScreen referrerPolicy="strict-origin-when-cross-origin" /> : (
          <button type="button" onClick={() => setPlaying(true)} aria-label={`Play ${video.title} by ${video.channel}`}>
            {!thumbnailFailed && <img src={`https://i.ytimg.com/vi/${video.id}/hqdefault.jpg`} alt={`${video.title} video preview`} loading="lazy" onError={() => setThumbnailFailed(true)} />}
            <span className="repair-video-play"><Play size={23} fill="currentColor" aria-hidden="true" /></span><span className="repair-video-youtube">YouTube</span>
          </button>
        )}
      </div>
      <div className="repair-video-copy"><p>{video.channel}</p><h4>{video.title}</h4><span>{video.scope}</span><a href={video.url} target="_blank" rel="noopener noreferrer">Watch on YouTube <ExternalLink size={13} aria-hidden="true" /></a></div>
    </article>
  );
}
