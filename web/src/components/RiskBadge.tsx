import type {RiskBand} from '../types';
export function RiskBadge({band}:{band:RiskBand}){return <span className={`badge ${band.toLowerCase()}`}>{band}</span>}
