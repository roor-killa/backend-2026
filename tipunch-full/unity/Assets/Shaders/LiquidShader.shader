// =============================================
//   Ti Punch Master — LiquidShader.shader
//   Shader HLSL pour le remplissage animé du verre
//   Compatible Built-in Render Pipeline
//   Version 2.0 · Martinique 2026
// =============================================

Shader "TiPunchMaster/LiquidFill"
{
    Properties
    {
        _LiquidColor ("Couleur du liquide",    Color)  = (1, 0.8, 0.2, 1)
        _FillLevel   ("Niveau (0=vide 1=plein)", Range(0,1)) = 0.5
        _Turbulence  ("Turbulence",            Range(0,1)) = 0.05
        _WaveSpeed   ("Vitesse d'ondulation",  Float)  = 1.0
        _WaveAmp     ("Amplitude de l'onde",   Float)  = 0.02
        _Opacity     ("Opacité",               Range(0,1)) = 0.88
        _RimColor    ("Couleur reflet",        Color)  = (1,1,1,0.3)
        _RimPower    ("Puissance reflet",      Range(0.5,8)) = 3.0
    }

    SubShader
    {
        Tags
        {
            "Queue"           = "Transparent"
            "RenderType"      = "Transparent"
            "IgnoreProjector" = "True"
        }

        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off
        Cull Back

        Pass
        {
            CGPROGRAM
            #pragma vertex   vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex   : POSITION;
                float3 normal   : NORMAL;
                float2 uv       : TEXCOORD0;
            };

            struct v2f
            {
                float4 pos      : SV_POSITION;
                float2 uv       : TEXCOORD0;
                float3 worldPos : TEXCOORD1;
                float3 normal   : TEXCOORD2;
                float3 viewDir  : TEXCOORD3;
            };

            fixed4 _LiquidColor;
            float  _FillLevel;
            float  _Turbulence;
            float  _WaveSpeed;
            float  _WaveAmp;
            float  _Opacity;
            fixed4 _RimColor;
            float  _RimPower;

            v2f vert (appdata v)
            {
                v2f o;
                o.pos      = UnityObjectToClipPos(v.vertex);
                o.uv       = v.uv;
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                o.normal   = UnityObjectToWorldNormal(v.normal);
                o.viewDir  = normalize(WorldSpaceViewDir(v.vertex));
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                // ─── Surface ondulée ──────────────────────────────────────
                float wave = sin(i.worldPos.x * 8.0 + _Time.y * _WaveSpeed * 3.0) * _WaveAmp
                           + sin(i.worldPos.z * 6.0 + _Time.y * _WaveSpeed * 2.0) * _WaveAmp * 0.5;

                float turbWave = sin(i.worldPos.x * 20.0 + _Time.y * 5.0) * _Turbulence * 0.04
                               + cos(i.worldPos.z * 18.0 + _Time.y * 4.5) * _Turbulence * 0.03;

                float liquidSurface = _FillLevel + wave + turbWave;

                // Masque : affiche le liquide seulement en dessous de la surface
                float mask = step(i.uv.y, liquidSurface);
                if (mask < 0.01) discard;

                // ─── Surface de la nappe (ligne de flottaison) ────────────
                float surfaceLine = abs(i.uv.y - liquidSurface);
                float surfaceGlow = smoothstep(0.015, 0.0, surfaceLine) * 0.4;

                // ─── Reflet rim (fresnel simplifié) ───────────────────────
                float rim = 1.0 - saturate(dot(i.viewDir, i.normal));
                rim = pow(rim, _RimPower);

                // ─── Assemblage couleur ───────────────────────────────────
                fixed4 col = _LiquidColor;

                // Léger dégradé vertical dans le verre (plus sombre au fond)
                float depth = saturate(i.uv.y / max(_FillLevel, 0.001));
                col.rgb *= lerp(0.65, 1.0, depth);

                // Reflet surface
                col.rgb += surfaceGlow * 0.6;

                // Rim
                col.rgb = lerp(col.rgb, _RimColor.rgb, rim * _RimColor.a);

                col.a = _Opacity;
                return col;
            }
            ENDCG
        }
    }

    FallBack "Transparent/Diffuse"
}
