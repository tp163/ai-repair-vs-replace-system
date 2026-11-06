import { z } from 'zod';
export const inputSchema = z.object({deviceId:z.string().min(1), confirmed:z.literal(true), symptoms:z.string().trim().min(8).max(3000), budget:z.number().positive().max(2000000).optional(), priority:z.enum(['balanced','battery','performance']).default('balanced'), answer:z.enum(['yes','no','unsure']).optional(), image:z.string().max(2800000).regex(/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/).optional(), replace:z.boolean().default(true)});
export type CaseInput=z.infer<typeof inputSchema>;
export const diagnosisSchema=z.object({category:z.enum(['screen','battery','charging','thermal','liquid','performance','unclear']), summary:z.string().max(800), alternatives:z.array(z.string().max(200)).max(4), confidence:z.enum(['low','medium']), observations:z.array(z.string().max(300)).max(6)});
export type Diagnosis=z.infer<typeof diagnosisSchema>;
export type Phone={id:string;brand:string;model:string;variant:string;price_lkr:number;ram_gb:number;storage_gb:number;battery_mah:number;chipset_tier:number;has_5g:boolean;os:string;display_size_in:number};
export type Pick={phone:Phone;category:string;reason:string;verified:boolean};
export type CaseResult={diagnosis:Diagnosis;safetyStop:boolean;question?:string;steps:string[];recommendations:Pick[];trace:string[];mode:'rules'|'live';imageReviewed:boolean;notice?:string;cost:{status:'unavailable';message:string}};
