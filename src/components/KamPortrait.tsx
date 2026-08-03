export function KamPortrait({ listening = false, speaking = false }: { listening?: boolean; speaking?: boolean }) {
  return (
    <div className={`kam-portrait ${listening ? 'is-listening' : ''} ${speaking ? 'is-speaking' : ''}`} aria-hidden="true">
      <div className="kam-portrait__halo" />
      <svg viewBox="0 0 180 220" role="presentation">
        <defs>
          <radialGradient id="skin" cx="47%" cy="34%" r="63%">
            <stop offset="0" stopColor="#efd2bd" />
            <stop offset=".5" stopColor="#a77870" />
            <stop offset="1" stopColor="#392d43" />
          </radialGradient>
          <linearGradient id="suit" x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="#5f6fff" />
            <stop offset=".48" stopColor="#171b35" />
            <stop offset="1" stopColor="#ff578e" />
          </linearGradient>
          <filter id="soft"><feGaussianBlur stdDeviation="3" /></filter>
          <filter id="glow"><feGaussianBlur stdDeviation="8" /></filter>
        </defs>
        <ellipse cx="90" cy="207" rx="74" ry="14" fill="#6de4ff" opacity=".32" filter="url(#glow)" />
        <path d="M31 211C37 161 56 145 88 145C124 145 145 167 151 211Z" fill="url(#suit)" />
        <path d="M66 142L89 181L113 143" fill="#11131c" stroke="#d7f7ff" strokeOpacity=".5" />
        <path d="M58 74C58 31 78 17 103 22C128 27 137 49 129 91C124 122 109 147 89 149C69 146 57 119 58 74Z" fill="url(#skin)" />
        <path d="M56 73C50 44 62 20 86 15C109 10 133 24 139 49C126 38 115 38 103 35C87 31 75 36 56 73Z" fill="#171522" />
        <path d="M55 63C49 79 52 96 60 109L57 79Z" fill="#1b1825" />
        <path d="M128 54C139 79 133 101 127 112L131 70Z" fill="#1b1825" />
        <path d="M73 78C79 73 86 73 91 78" stroke="#362935" strokeWidth="3" strokeLinecap="round" />
        <path d="M101 78C108 73 115 74 119 79" stroke="#362935" strokeWidth="3" strokeLinecap="round" />
        <ellipse cx="82" cy="81" rx="3.8" ry="3" fill="#9ff1ff" />
        <ellipse cx="111" cy="82" rx="3.8" ry="3" fill="#9ff1ff" />
        <path d="M96 80C93 92 90 101 97 104" stroke="#795c5e" strokeWidth="2" strokeLinecap="round" />
        <path className="kam-mouth" d="M80 119C91 126 103 126 113 118" stroke="#4e293b" strokeWidth="3" strokeLinecap="round" fill="none" />
        <path d="M68 66C76 62 86 62 92 66M101 67C108 63 118 64 123 68" stroke="#211b28" strokeWidth="3" strokeLinecap="round" />
        <ellipse cx="93" cy="96" rx="55" ry="69" fill="none" stroke="#9aefff" strokeOpacity=".18" />
        <path d="M39 105C25 76 32 42 56 22" stroke="#73eaff" strokeOpacity=".42" strokeWidth="2" />
        <circle cx="36" cy="107" r="5" fill="#eaff76" />
      </svg>
      <div className="kam-portrait__scan" />
    </div>
  )
}
