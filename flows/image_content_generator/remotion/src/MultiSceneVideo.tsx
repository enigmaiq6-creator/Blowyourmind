import React, { useMemo } from 'react';
import { Sequence, useVideoConfig, useCurrentFrame, interpolate, Easing } from 'remotion';
import { MapRender } from './MapRender';
import type { HexIconData, RouteData, RegionData } from './MapOverlays';

interface NarrationCue {
  word: string;
  startMs: number;
  endMs: number;
  eventType?: 'pin_drop' | 'label_flash' | 'vignette_slide' | 'arrow_animate' | 'camera_zoom';
  target?: string;
}

interface SceneProps {
  visualType?: string;
  imageFile?: string;
  latitude: number;
  longitude: number;
  zoom: number;
  pitch: number;
  bearing: number;
  highlightRegion?: string;
  arrowDirection?: string;
  floatingLabel?: string;
  pins?: { latitude: number; longitude: number; label: string; value?: string }[];
  vignettes?: { icon: string; title: string; value: string }[];
  cameraPath?: { latitude: number; longitude: number; zoom: number; pitch: number; bearing: number }[];
  audioDurationMs: number;
  narrationCues?: NarrationCue[];
  subtitleWords?: { word: string; startMs: number; endMs: number }[];
  hexIcons?: HexIconData[];
  routes?: RouteData[];
  regions?: RegionData[];
  mapStyle?: 'dark' | 'satellite';
  scanEffect?: boolean;
  lowerThirdData?: { icon: string; label: string; value: string }[];
  geopolitical?: any;
  sceneOverlay?: any;
}

interface MultiSceneProps {
  scenes: SceneProps[];
  transitionFrames?: number;
}

export const MultiSceneVideo: React.FC<MultiSceneProps> = ({
  scenes,
  transitionFrames = 12,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const sceneTimings = useMemo(() => {
    let totalFrames = 0;
    return scenes.map((scene) => {
      const sceneFrames = Math.ceil((scene.audioDurationMs / 1000) * fps);
      const startFrame = totalFrames;
      totalFrames += sceneFrames;
      return { startFrame, endFrame: startFrame + sceneFrames, sceneFrames };
    });
  }, [scenes, fps]);

  return (
    <div style={{ width: 1080, height: 1920, position: 'relative', backgroundColor: '#050505' }}>
      {scenes.map((scene, i) => {
        const timing = sceneTimings[i];
        const isActive = frame >= timing.startFrame && frame < timing.endFrame;
        const isPast = frame >= timing.endFrame;

        if (!isActive && !isPast) return null;

        const fadeOutDuration = Math.min(transitionFrames, timing.sceneFrames * 0.15);
        const opacity = isActive
          ? 1
          : Math.max(0, interpolate(
              frame - (timing.endFrame - fadeOutDuration),
              [0, fadeOutDuration],
              [1, 0],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.ease) }
            ));

        const scale = isActive
          ? interpolate(frame - timing.startFrame, [0, 15], [0.97, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
              easing: Easing.out(Easing.ease),
            })
          : interpolate(frame - (timing.endFrame - fadeOutDuration), [0, fadeOutDuration], [1, 1.03], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
              easing: Easing.in(Easing.ease),
            });

        const sceneCues = scene.narrationCues?.filter(c => {
          const sceneStartMs = (timing.startFrame / fps) * 1000;
          const sceneEndMs = (timing.endFrame / fps) * 1000;
          return c.startMs >= sceneStartMs && c.endMs <= sceneEndMs;
        });

        return (
          <div
            key={`scene-${i}`}
            style={{
              position: 'absolute', inset: 0,
              opacity,
              transform: `scale(${scale})`,
              pointerEvents: 'none',
              zIndex: isActive ? scenes.length - i : 0,
            }}
          >
            <Sequence
              name={`Scene ${i + 1}`}
              from={timing.startFrame}
              durationInFrames={timing.sceneFrames}
            >
              <MapRender
                visualType={scene.visualType}
                imageFile={scene.imageFile || ''}
                latitude={scene.latitude}
                longitude={scene.longitude}
                zoom={scene.zoom}
                pitch={scene.pitch}
                bearing={scene.bearing}
                highlightRegion={scene.highlightRegion || 'none'}
                arrowDirection={scene.arrowDirection || 'none'}
                floatingLabel={scene.floatingLabel || 'none'}
                pins={scene.pins || []}
                vignettes={scene.vignettes || []}
                cameraPath={scene.cameraPath || []}
                narrationCues={sceneCues || []}
                subtitleWords={scene.subtitleWords || []}
                hexIcons={scene.hexIcons || []}
                routes={scene.routes || []}
                regions={scene.regions || []}
                mapStyle={scene.mapStyle || 'dark'}
                scanEffect={scene.scanEffect || false}
                lowerThirdData={scene.lowerThirdData || []}
                sceneStartMs={(timing.startFrame / fps) * 1000}
                geopolitical={scene.geopolitical}
                sceneOverlay={scene.sceneOverlay}
              />
            </Sequence>
          </div>
        );
      })}
    </div>
  );
};
