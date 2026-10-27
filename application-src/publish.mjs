import {cp,mkdir} from 'node:fs/promises';
await mkdir('../application-assets',{recursive:true});
await cp('dist/application-assets','../application-assets',{recursive:true});
await cp('dist/index.html','../application.html');
