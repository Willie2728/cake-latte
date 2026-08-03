export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`brand ${compact ? 'brand--compact' : ''}`} aria-label="Cake-Latte by Verloray AI OS">
      <img src="/constellate-mark.svg" alt="" className="brand__mark" />
      <div className="brand__type">
        <strong>CAKE-LATTE</strong>
        {!compact && <span>BY VERLORAY AI OS</span>}
      </div>
    </div>
  )
}
