import { useId } from 'react';
import type { Phone } from './catalogue-data';

type Palette = {
  body: string;
  edge: string;
  screen: string;
  glow: string;
  cameras: [number, number][];
};

const palettes: Record<string, Palette> = {
  Apple: { body: '#a8c6da', edge: '#365370', screen: '#234d79', glow: '#aeeafb', cameras: [[42, 42], [63, 64]] },
  Samsung: { body: '#d2c4f3', edge: '#6b5c8e', screen: '#3a33a8', glow: '#edb8fd', cameras: [[40, 43], [40, 68], [40, 93]] },
  Xiaomi: { body: '#51635e', edge: '#152d2a', screen: '#135b53', glow: '#b0f5b5', cameras: [[41, 43], [41, 71], [65, 55]] },
  Poco: { body: '#b0bcc9', edge: '#46536b', screen: '#55401d', glow: '#ffd677', cameras: [[41, 43], [66, 43], [42, 68]] },
  Google: { body: '#bcd0ed', edge: '#5c6b92', screen: '#29438f', glow: '#b9d2ff', cameras: [[48, 49], [68, 49]] },
};

export default function PhoneIllustration({ phone, className }: { phone: Phone; className?: string }) {
  const id = useId();
  const palette = palettes[phone.brand] ?? palettes.Google;

  return (
    <svg viewBox="0 0 252 258" aria-hidden="true" className={className}>
      <defs>
        <linearGradient id={`${id}-body`} x2="1" y2="1">
          <stop stopColor={palette.body} />
          <stop offset="1" stopColor={palette.edge} />
        </linearGradient>
        <linearGradient id={`${id}-screen`} x1="0%" y1="0%" x2="80%" y2="100%">
          <stop stopColor="#101826" />
          <stop offset=".53" stopColor={palette.screen} />
          <stop offset="1" stopColor="#0d1222" />
        </linearGradient>
        <linearGradient id={`${id}-wallpaper`} x1="5%" y1="95%" x2="100%" y2="5%">
          <stop stopColor={palette.screen} />
          <stop offset=".58" stopColor={palette.glow} />
          <stop offset="1" stopColor={palette.edge} />
        </linearGradient>
        <clipPath id={`${id}-display`}>
          <rect x="119" y="26" width="99" height="205" rx="15" />
        </clipPath>
      </defs>
      <ellipse cx="126" cy="242" rx="101" ry="7" fill="#0f172a" opacity=".09" />
      <g transform="rotate(-7 75 127)">
        <rect x="20" y="16" width="111" height="219" rx="21" fill={palette.edge} />
        <rect x="23" y="19" width="105" height="213" rx="19" fill={`url(#${id}-body)`} stroke="#fff" strokeOpacity=".38" />
        {phone.brand === 'Google' && <rect x="32" y="35" width="88" height="28" rx="13" fill={palette.edge} />}
        {palette.cameras.map(([cx, cy]) => (
          <g key={`${cx}-${cy}`}>
            <circle cx={cx} cy={cy} r="10" fill={palette.edge} stroke={palette.body} />
            <circle cx={cx} cy={cy} r="7.2" fill="#111827" />
            <circle cx={cx - 1.5} cy={cy - 1.5} r="2.6" fill="#4b6b97" opacity=".55" />
          </g>
        ))}
        <circle cx="86" cy="42" r="3.2" fill="#f8fafc" opacity=".75" />
      </g>
      <g transform="rotate(6 168 128)">
        <rect x="113" y="20" width="111" height="217" rx="21" fill="#10151f" stroke={palette.edge} strokeWidth="2" />
        <g clipPath={`url(#${id}-display)`}>
          <rect x="119" y="26" width="99" height="205" fill={`url(#${id}-screen)`} />
          <path d="M111 207C126 181 163 172 195 138C216 115 217 80 227 70V240H111Z" fill={`url(#${id}-wallpaper)`} />
          <path d="M104 183C152 130 197 150 231 85L231 128C193 175 138 170 104 209Z" fill={palette.glow} opacity=".58" />
          <path d="M115 216C141 180 189 182 223 140" fill="none" stroke="#fff" strokeOpacity=".4" strokeWidth="2" />
        </g>
        {phone.brand === 'Apple'
          ? <path d="M149 26h39v3a7 7 0 0 1-7 7h-25a7 7 0 0 1-7-7Z" fill="#10151f" />
          : <circle cx="168.5" cy="33" r="3.4" fill="#10151f" />}
        <rect x="150" y="224" width="37" height="2.5" rx="1.25" fill="#fff" opacity=".65" />
      </g>
    </svg>
  );
}
