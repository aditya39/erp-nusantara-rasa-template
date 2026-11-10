import{a as F,b as k}from"./chunk-QY53RKEX.js";import{a as c}from"./chunk-65OYOH4Y.js";import{N as D,P as M,R as s}from"./chunk-E3NTVW4X.js";import{d as N}from"./chunk-IWZG5XKJ.js";import{D as f,F as u,Ha as y,S as m,T as a,V as h,Va as T,W as p,_ as b,ib as l,kb as e,n as g,o as x,ob as r,p as v,r as d,ta as I}from"./chunk-OFCKUUSY.js";var j=(()=>{class t extends k{pcFluid=d(c,{optional:!0,host:!0,skipSelf:!0});fluid=e(void 0,{transform:r});variant=e();size=e();inputSize=e();pattern=e();min=e();max=e();step=e();minlength=e();maxlength=e();$variant=l(()=>this.variant()||this.config.inputStyle()||this.config.inputVariant());get hasFluid(){return this.fluid()??!!this.pcFluid}static \u0275fac=(()=>{let n;return function(o){return(n||(n=u(t)))(o||t)}})();static \u0275dir=a({type:t,inputs:{fluid:[1,"fluid"],variant:[1,"variant"],size:[1,"size"],inputSize:[1,"inputSize"],pattern:[1,"pattern"],min:[1,"min"],max:[1,"max"],step:[1,"step"],minlength:[1,"minlength"],maxlength:[1,"maxlength"]},features:[p]})}return t})();var S=`
    .p-inputtext {
        font-family: inherit;
        font-feature-settings: inherit;
        font-size: 1rem;
        color: dt('inputtext.color');
        background: dt('inputtext.background');
        padding-block: dt('inputtext.padding.y');
        padding-inline: dt('inputtext.padding.x');
        border: 1px solid dt('inputtext.border.color');
        transition:
            background dt('inputtext.transition.duration'),
            color dt('inputtext.transition.duration'),
            border-color dt('inputtext.transition.duration'),
            outline-color dt('inputtext.transition.duration'),
            box-shadow dt('inputtext.transition.duration');
        appearance: none;
        border-radius: dt('inputtext.border.radius');
        outline-color: transparent;
        box-shadow: dt('inputtext.shadow');
    }

    .p-inputtext:enabled:hover {
        border-color: dt('inputtext.hover.border.color');
    }

    .p-inputtext:enabled:focus {
        border-color: dt('inputtext.focus.border.color');
        box-shadow: dt('inputtext.focus.ring.shadow');
        outline: dt('inputtext.focus.ring.width') dt('inputtext.focus.ring.style') dt('inputtext.focus.ring.color');
        outline-offset: dt('inputtext.focus.ring.offset');
    }

    .p-inputtext.p-invalid {
        border-color: dt('inputtext.invalid.border.color');
    }

    .p-inputtext.p-variant-filled {
        background: dt('inputtext.filled.background');
    }

    .p-inputtext.p-variant-filled:enabled:hover {
        background: dt('inputtext.filled.hover.background');
    }

    .p-inputtext.p-variant-filled:enabled:focus {
        background: dt('inputtext.filled.focus.background');
    }

    .p-inputtext:disabled {
        opacity: 1;
        background: dt('inputtext.disabled.background');
        color: dt('inputtext.disabled.color');
    }

    .p-inputtext::placeholder {
        color: dt('inputtext.placeholder.color');
    }

    .p-inputtext.p-invalid::placeholder {
        color: dt('inputtext.invalid.placeholder.color');
    }

    .p-inputtext-sm {
        font-size: dt('inputtext.sm.font.size');
        padding-block: dt('inputtext.sm.padding.y');
        padding-inline: dt('inputtext.sm.padding.x');
    }

    .p-inputtext-lg {
        font-size: dt('inputtext.lg.font.size');
        padding-block: dt('inputtext.lg.padding.y');
        padding-inline: dt('inputtext.lg.padding.x');
    }

    .p-inputtext-fluid {
        width: 100%;
    }
`;var E=`
    ${S}

    /* For PrimeNG */
   .p-inputtext.ng-invalid.ng-dirty {
        border-color: dt('inputtext.invalid.border.color');
    }

    .p-inputtext.ng-invalid.ng-dirty::placeholder {
        color: dt('inputtext.invalid.placeholder.color');
    }
`,B={root:({instance:t})=>["p-inputtext p-component",{"p-filled":t.$filled(),"p-inputtext-sm":t.pSize==="small","p-inputtext-lg":t.pSize==="large","p-invalid":t.invalid(),"p-variant-filled":t.$variant()==="filled","p-inputtext-fluid":t.hasFluid}]},z=(()=>{class t extends D{name="inputtext";style=E;classes=B;static \u0275fac=(()=>{let n;return function(o){return(n||(n=u(t)))(o||t)}})();static \u0275prov=g({token:t,factory:t.\u0275fac})}return t})();var w=new v("INPUTTEXT_INSTANCE"),nt=(()=>{class t extends F{componentName="InputText";hostName="";ptInputText=e();pInputTextPT=e();pInputTextUnstyled=e();bindDirectiveInstance=d(s,{self:!0});$pcInputText=d(w,{optional:!0,skipSelf:!0})??void 0;ngControl=d(N,{optional:!0,self:!0});pcFluid=d(c,{optional:!0,host:!0,skipSelf:!0});pSize;variant=e();fluid=e(void 0,{transform:r});invalid=e(void 0,{transform:r});$variant=l(()=>this.variant()||this.config.inputStyle()||this.config.inputVariant());_componentStyle=d(z);constructor(){super(),f(()=>{let n=this.ptInputText()||this.pInputTextPT();n&&this.directivePT.set(n)}),f(()=>{this.pInputTextUnstyled()&&this.directiveUnstyled.set(this.pInputTextUnstyled())})}onAfterViewInit(){this.writeModelValue(this.ngControl?.value??this.el.nativeElement.value),this.cd.detectChanges()}onAfterViewChecked(){this.bindDirectiveInstance.setAttrs(this.ptm("root"))}onDoCheck(){this.writeModelValue(this.ngControl?.value??this.el.nativeElement.value)}onInput(){this.writeModelValue(this.ngControl?.value??this.el.nativeElement.value)}get hasFluid(){return this.fluid()??!!this.pcFluid}get dataP(){return this.cn({invalid:this.invalid(),fluid:this.hasFluid,filled:this.$variant()==="filled",[this.pSize]:this.pSize})}static \u0275fac=function(i){return new(i||t)};static \u0275dir=a({type:t,selectors:[["","pInputText",""]],hostVars:3,hostBindings:function(i,o){i&1&&I("input",function(){return o.onInput()}),i&2&&(b("data-p",o.dataP),y(o.cx("root")))},inputs:{hostName:"hostName",ptInputText:[1,"ptInputText"],pInputTextPT:[1,"pInputTextPT"],pInputTextUnstyled:[1,"pInputTextUnstyled"],pSize:"pSize",variant:[1,"variant"],fluid:[1,"fluid"],invalid:[1,"invalid"]},features:[T([z,{provide:w,useExisting:t},{provide:M,useExisting:t}]),h([s]),p]})}return t})(),it=(()=>{class t{static \u0275fac=function(i){return new(i||t)};static \u0275mod=m({type:t});static \u0275inj=x({})}return t})();export{j as a,nt as b,it as c};
