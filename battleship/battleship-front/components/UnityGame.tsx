'use client';

import { useEffect, useRef, useState } from 'react';
import styles from './UnityGame.module.css';

type ShotResult = {
  row: number;
  col: number;
  result: 'hit' | 'miss' | 'sunk';
};

type UnityGameProps = {
  className?: string;
  onCellSelected?: (row: number, col: number) => void;
  shotResultToSend?: ShotResult | null;
};

type UnityConfig = {
  dataUrl: string;
  frameworkUrl: string;
  codeUrl: string;
  streamingAssetsUrl?: string;
  companyName?: string;
  productName?: string;
  productVersion?: string;
};

type UnityInstance = {
  SendMessage: (objectName: string, methodName: string, value?: string) => void;
  Quit?: () => Promise<void>;
};

declare global {
  interface Window {
    createUnityInstance?: (
      canvas: HTMLCanvasElement,
      config: UnityConfig,
      onProgress?: (progress: number) => void
    ) => Promise<UnityInstance>;
    onCellSelected?: (row: number, col: number) => void;
  }
}

const UNITY_BUILD_AVAILABLE = process.env.NEXT_PUBLIC_UNITY_BUILD === 'true';

function UnityPlaceholder({ className }: { className?: string }) {
  return (
    <div
      className={className}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#0b1320',
        color: '#4a9eff',
        flexDirection: 'column',
        gap: '12px',
        borderRadius: '8px',
        border: '2px dashed #1e3a5f',
      }}
    >
      <span style={{ fontSize: '2rem' }}>⚓</span>
      <p style={{ margin: 0, fontSize: '1rem' }}>Jeu 3D non disponible</p>
      <p style={{ margin: 0, fontSize: '0.75rem', color: '#6b8cae' }}>
        Build Unity WebGL non déployé
      </p>
    </div>
  );
}

function UnityGame({ className, onCellSelected, shotResultToSend }: UnityGameProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const unityInstanceRef = useRef<UnityInstance | null>(null);
  const [loadingProgress, setLoadingProgress] = useState<number>(0);
  const [isReady, setIsReady] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!UNITY_BUILD_AVAILABLE) return;

    let disposed = false;

    window.onCellSelected = (row: number, col: number) => {
      onCellSelected?.(row, col);
    };

    const loadUnity = async () => {
      if (!canvasRef.current) return;

      try {
        const existingScript = document.querySelector<HTMLScriptElement>('script[data-unity-loader="game"]');

        if (!existingScript) {
          const loaderScript = document.createElement('script');
          loaderScript.src = '/unity/Build/game.loader.js';
          loaderScript.async = true;
          loaderScript.dataset.unityLoader = 'game';

          await new Promise<void>((resolve, reject) => {
            loaderScript.onload = () => resolve();
            loaderScript.onerror = () => reject(new Error('Impossible de charger game.loader.js'));
            document.body.appendChild(loaderScript);
          });
        }

        if (!window.createUnityInstance) {
          throw new Error('createUnityInstance introuvable. Verifie le build Unity WebGL.');
        }

        const config: UnityConfig = {
          dataUrl: '/unity/Build/game.data',
          frameworkUrl: '/unity/Build/game.framework.js',
          codeUrl: '/unity/Build/game.wasm',
          streamingAssetsUrl: '/unity/StreamingAssets',
          companyName: 'UA-L2',
          productName: 'BatailleNavale3D',
          productVersion: '1.0.0',
        };

        const instance = await window.createUnityInstance(
          canvasRef.current,
          config,
          (progress) => {
            if (!disposed) setLoadingProgress(progress);
          }
        );

        if (disposed) {
          await instance.Quit?.();
          return;
        }

        unityInstanceRef.current = instance;
        setIsReady(true);
      } catch (e) {
        const message = e instanceof Error ? e.message : 'Erreur inconnue pendant le chargement Unity';
        setError(message);
      }
    };

    void loadUnity();

    return () => {
      disposed = true;
      window.onCellSelected = undefined;

      const instance = unityInstanceRef.current;
      unityInstanceRef.current = null;
      setIsReady(false);

      if (instance?.Quit) {
        void instance.Quit();
      }
    };
  }, [onCellSelected]);

  useEffect(() => {
    if (!shotResultToSend || !unityInstanceRef.current || !isReady) return;

    unityInstanceRef.current.SendMessage(
      'GameManager',
      'OnShotResult',
      JSON.stringify(shotResultToSend)
    );
  }, [shotResultToSend, isReady]);

  if (!UNITY_BUILD_AVAILABLE) {
    return <UnityPlaceholder className={className} />;
  }

  return (
    <div className={className}>
      {!isReady && !error ? (
        <p>Chargement Unity: {Math.round(loadingProgress * 100)}%</p>
      ) : null}
      {error ? <p>Erreur Unity: {error}</p> : null}
      <canvas
        ref={canvasRef}
        id="unity-canvas"
        className={styles.unityCanvas}
      />
    </div>
  );
}

export default UnityGame;
