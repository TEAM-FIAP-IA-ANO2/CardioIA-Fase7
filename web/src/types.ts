export type RiskBand='BAIXO'|'MODERADO'|'ALTO';
export type PatientData={idade_media:number;carga_sistema:number;tempo_espera:number;fc_media:number;spo2_media:number;pa_sistolica:number;temperatura:number;densidade_eventos:number;eventos_24h:number;disponibilidade_recursos:number};
export type Protocol={protocol_id:string;action:string;reason:string;severity:'informativa'|'atencao'|'critica'};
export type Analysis={execution_id:string;probability:number;predicted_class:0|1;risk_band:RiskBand;protocols:Protocol[];evidence:string[];rationale:string;human_review_required:boolean;disclaimer:string};
export type History={reading_id:number;device_id:string;captured_at:string;received_at:string;probability:number;risk_band:RiskBand;payload:PatientData};
