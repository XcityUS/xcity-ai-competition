import React from 'react';
import {createRoot} from 'react-dom/client';
import Application from './Application';
import './style.css';
const query=new URLSearchParams(location.search);
const isPrivate=/^#application=XCITY-/.test(location.hash);
if(query.get('embed')!=='1'&&!isPrivate){
 let lang=query.get('lang');
 if(!['en','zh'].includes(lang))try{lang=localStorage.getItem('xcity-lang');}catch{}
 const url=new URL('practice.html',location.href);
 url.searchParams.set('lang',lang==='zh'?'zh':'en');url.hash='apply';
 location.replace(url.href);
}else createRoot(document.getElementById('root')).render(<Application/>);
