export default function IntroBackdrop() {
  return (
    <div className="diagnosis-intro-backdrop" aria-hidden="true">
      <svg viewBox="0 0 1200 900" preserveAspectRatio="xMidYMid slice" className="diagnosis-intro-stars">
        <defs><filter id="diagnosis-star-glow"><feGaussianBlur stdDeviation="2.2" /></filter></defs>
        {Array.from({ length: 150 }, (_, index) => {
          const x = ((index * 7919 + 1723) % 12000) / 10;
          const y = ((index * 4421 + 629) % 9000) / 10;
          const radius = index % 11 === 0 ? 1.9 : index % 3 === 0 ? 1.1 : .6;
          const opacity = .22 + (index % 7) * .1;
          return <g key={index} opacity={opacity}>{index % 11 === 0 && <circle cx={x} cy={y} r={4} fill="#7dd3fc" filter="url(#diagnosis-star-glow)" />}<circle cx={x} cy={y} r={radius} fill={index % 3 === 0 ? '#a5dffb' : '#eef8ff'} /></g>;
        })}
      </svg>
    </div>
  );
}
