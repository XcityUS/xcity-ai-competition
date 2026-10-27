'use client';
import {useEffect,useState} from 'react';
import LegacyApplication from './LegacyApplication';
const API=location.hostname==='localhost'||location.hostname==='127.0.0.1'?'http://127.0.0.1:8787':'https://xcity-practice-applications.jingyuan-huang.chatgpt.site';
const SITE='https://xcityus.github.io/xcity-ai-competition/';
export default function Application(){
 useEffect(()=>{if(!/^#application=XCITY-/.test(location.hash)&&new URLSearchParams(location.search).get('embed')!=='1'){const lang=new URLSearchParams(location.search).get('lang')==='zh'?'zh':'en';location.replace('practice.html?lang='+lang+'#apply');}},[]);
 if(/^#application=XCITY-/.test(location.hash))return <LegacyApplication/>;
 return <Registration/>;
}
function Registration(){
 const[zh,setZh]=useState(new URLSearchParams(location.search).get('lang')==='zh'),[token,setToken]=useState(''),[accepting,setAccepting]=useState(true),[busy,setBusy]=useState(false),[receipt,setReceipt]=useState(''),[error,setError]=useState('');
 const open=true;
 const sessionCache='xcity-application-session-v1';
 const receiptCache='xcity-registration-receipt-v1';
 async function connect(){
  setError('');
  try{
   const previous=sessionStorage.getItem(receiptCache);if(previous&&/^XCITY-[A-F0-9]{16}$/.test(previous)){setReceipt(previous);return;}
   try{const c=JSON.parse(sessionStorage.getItem(sessionCache)||'null');if(c&&/^[a-f0-9]{64}$/.test(c.token)&&Date.now()-c.createdAt<50*60*1000){setToken(c.token);setAccepting(!c.deadline||Date.now()<=Date.parse(c.deadline));return;}}catch{}
   const r=await fetch(API+'/api/session',{credentials:'omit',method:'POST'});const d=await r.json();
   if(!r.ok){setError(r.status===429?'rate':'connection');return;}
   setToken(d.token);setAccepting(d.registrationOpen!==false);
   try{sessionStorage.setItem(sessionCache,JSON.stringify({token:d.token,createdAt:Date.now(),deadline:d.registrationDeadline}));}catch{}
  }catch{setError('connection');}
 }

 const L=(en:string,cn:string)=>zh?cn:en;
 useEffect(()=>{const q=new URLSearchParams(location.search);if(q.get('embed')==='1')document.documentElement.classList.add('embedded');document.documentElement.lang=zh?'zh':'en';const send=()=>{if(parent!==window)parent.postMessage({type:'xcity-application-height',height:document.body.scrollHeight},location.origin);};const observer=new ResizeObserver(send);observer.observe(document.body);const language=(event:MessageEvent)=>{if(event.source===parent&&event.origin===location.origin&&event.data?.type==='xcity-language'){setZh(event.data.lang==='zh');document.documentElement.lang=event.data.lang==='zh'?'zh':'en';}};addEventListener('message',language);connect();return()=>{observer.disconnect();removeEventListener('message',language);};},[]);
 async function register(event:React.FormEvent<HTMLFormElement>){event.preventDefault();if(!token)return;setBusy(true);setError('');const data=Object.fromEntries(new FormData(event.currentTarget));try{const r=await fetch(API+'/api/register',{credentials:'omit',method:'POST',headers:{'Content-Type':'application/json','x-form-token':token},body:JSON.stringify({...data,privacy:data.privacy==='on'})});const d=await r.json();if(!r.ok){if(r.status===403){try{sessionStorage.removeItem(sessionCache);}catch{}setToken('');}setError(r.status===429?'rate':'submit');return;}try{sessionStorage.removeItem(sessionCache);sessionStorage.setItem(receiptCache,d.id);}catch{}setReceipt(d.id);}catch{setError('submit');}finally{setBusy(false);}}
 return <><nav className="top"><a href={SITE+'practice.html'}>XCITY / {L('Design Practice Call','设计机构征集')}</a><button onClick={()=>{setZh(!zh);document.documentElement.lang=zh?'en':'zh';}}>{zh?'EN':'中文'}</button></nav><main className="shell registration"><h1>{open?L('Apply online','在线申请'):L('Register online','在线登记')}</h1><p className="lead">{open?L('Complete the details below. We will email your private materials link. Complete the form and upload the required materials there, then submit for stage-one review.','请填写以下信息。我们将通过邮件发送专属材料链接；请在链接中填写表格、上传所需材料并提交申请。'):L('The Design Practice Call is not open yet. Leave your details and we will contact you by email when applications open.','设计机构征集尚未正式开放。留下信息，开放后我们将通过邮件联系你。')}</p>{receipt?<div className="receipt" role="status"><h2>{open?L('Application received','申请已收到'):L('Interest registered','关注登记成功')}</h2><p>{open?L('We will send your private materials link to the email provided. Complete and submit your application there by 31 January 2027, 23:59 UTC. This receipt is not eligibility or shortlist approval.','我们将向你填写的邮箱发送专属材料链接。请于 2027 年 1 月 31 日 23:59 UTC 前填写、上传并提交完整申请。此回执不代表资格通过或入围。'):L('We will contact you at the email address provided when applications open.','正式开放后，我们将通过你填写的邮箱联系你。')}</p><small>{L('Reference: ','登记编号：')}{receipt}</small></div>:<form className="panel simple-form" onSubmit={register}><div className="field-grid"><label>{L('Institution name','机构名称')}<input name="org" required maxLength={200} autoComplete="organization"/></label><label>{L('Country / region','国家／地区')}<input name="country" required maxLength={200} autoComplete="country-name"/></label><label>{L('Contact name','联系人')}<input name="contact" required maxLength={200} autoComplete="name"/></label><label>{L('Email','邮箱')}<input name="email" required type="email" maxLength={200} autoComplete="email"/></label></div><label className="check"><input name="privacy" type="checkbox" required/>{L('I agree that XCITY may store these details privately and contact me about this call.','我同意 XCITY 私下保存以上信息，并就本次征集与我联系。')}</label><button className="primary" disabled={!token||busy||!accepting}>{!accepting?L('Registration closed','登记已截止'):busy?L('Saving…','正在保存…'):open?L('Apply online','在线申请'):L('Register online','在线登记')}</button></form>}{error&&<div className="feedback" role="alert"><p>{error==='rate'?L('The form has been accessed frequently. Please wait and retry, or contact competition@xcity.ai.','表单访问较频繁，请稍后重试，或联系 competition@xcity.ai。'):L('Your application has not been confirmed. Check the connection and retry, or contact competition@xcity.ai.','本次申请尚未确认收件。请检查连接后重试，或联系 competition@xcity.ai。')}</p><button type="button" onClick={()=>connect()}>{L('Reconnect','重新连接')}</button></div>}</main></>;
}
