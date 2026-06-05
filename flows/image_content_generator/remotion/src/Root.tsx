import { Composition, continueRender, delayRender, staticFile } from 'remotion';
import { useEffect, useState } from 'react';
import { Subtitles } from './Subtitles';
import { MapRender } from './MapRender';
import { MultiSceneVideo } from './MultiSceneVideo';
import { DataVisualization } from './DataVisualization';
import { SplitMap } from './SplitMap';
import { HexDataGrid } from './HexDataGrid';

export const RemotionRoot: React.FC = () => {
  const [fontHandle] = useState(() => delayRender('Montserrat font'));
  useEffect(() => {
    const font = new FontFace(
      'Montserrat Black',
      `url(${staticFile('fonts/Montserrat-Black.ttf')}) format('truetype')`
    );
    font.load().then(() => {
      document.fonts.add(font);
      continueRender(fontHandle);
    }).catch(() => continueRender(fontHandle));
  }, [fontHandle]);

  return (
    <>
      <Composition
        id="Subtitles"
        component={Subtitles}
        durationInFrames={1500}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          words: [
            { text: "BlowYourMind", start: 0, end: 1000 },
            { text: "Mind", start: 1000, end: 2000 },
            { text: "Blowing", start: 2000, end: 3000 }
          ]
        }}
        calculateMetadata={({ props }) => {
          const words = (props as any).words || [];
          const lastMs = words.length > 0 ? words[words.length - 1].end : 3000;
          const frames = Math.ceil((lastMs / 1000) * 30) + 30;
          return { durationInFrames: Math.max(frames, 30) };
        }}
      />

      <Composition
        id="MapRender"
        component={MapRender}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          audioDurationMs: 8000,
          latitude: 4.570868,
          longitude: -74.297333,
          zoom: 5.2,
          pitch: 45,
          bearing: -10,
          highlightRegion: 'Colombia',
          arrowDirection: 'none',
          floatingLabel: '52.32M'
        }}
        calculateMetadata={({ props }) => {
          const audioMs = (props as any).audioDurationMs || 8000;
          const frames = Math.ceil((audioMs / 1000) * 30);
          return { durationInFrames: Math.max(frames, 30) };
        }}
      />

      <Composition
        id="MapRenderPro"
        component={MapRender}
        durationInFrames={450}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          audioDurationMs: 15000,
          latitude: 40.7128,
          longitude: -74.006,
          zoom: 5.5,
          pitch: 50,
          bearing: 15,
          highlightRegion: 'USA',
          arrowDirection: 'from: Pacific Ocean, to: Atlantic Ocean',
          floatingLabel: 'NEW YORK CITY',
          pins: [
            { latitude: 40.7128, longitude: -74.006, label: 'New York', value: '8.4M' },
            { latitude: 40.758, longitude: -73.9855, label: 'Times Sq', value: '360K/day' },
            { latitude: 40.7484, longitude: -73.9857, label: 'Empire State', value: '443m' },
          ],
          vignettes: [
            { icon: '🏙️', title: 'POPULATION', value: '8.4 Million' },
            { icon: '🗽', title: 'FOUNDED', value: '1624' },
            { icon: '🌊', title: 'COASTLINE', value: '930 KM' },
          ],
          cameraPath: [
            { latitude: 39.8283, longitude: -98.5795, zoom: 4.2, pitch: 30, bearing: 0 },
            { latitude: 41.0, longitude: -76.0, zoom: 6.5, pitch: 40, bearing: 10 },
            { latitude: 40.7128, longitude: -74.006, zoom: 11.5, pitch: 60, bearing: -15 },
            { latitude: 40.7484, longitude: -73.9857, zoom: 13.5, pitch: 65, bearing: -10 },
            { latitude: 40.7128, longitude: -74.006, zoom: 12.0, pitch: 55, bearing: -5 },
            { latitude: 41.0, longitude: -76.0, zoom: 6.5, pitch: 40, bearing: 10 },
            { latitude: 39.8283, longitude: -98.5795, zoom: 4.2, pitch: 30, bearing: 0 },
          ],
        }}
        calculateMetadata={({ props }) => {
          const audioMs = (props as any).audioDurationMs || 15000;
          const frames = Math.ceil((audioMs / 1000) * 30);
          return { durationInFrames: Math.max(frames, 30) };
        }}
      />

      <Composition
        id="MultiSceneVideo"
        component={MultiSceneVideo}
        durationInFrames={1500}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          scenes: [
            {
              audioDurationMs: 8000,
              latitude: 4.570868,
              longitude: -74.297333,
              zoom: 5.2,
              pitch: 45,
              bearing: -10,
              highlightRegion: 'Colombia',
              floatingLabel: '52.32M',
            },
            {
              audioDurationMs: 8000,
              latitude: 40.7128,
              longitude: -74.006,
              zoom: 11.5,
              pitch: 60,
              bearing: -15,
              highlightRegion: 'USA',
              floatingLabel: '8.4M PEOPLE',
            },
          ],
          transitionFrames: 12,
        }}
        calculateMetadata={({ props }) => {
          const p = props as any;
          const scenes = p.scenes || [];
          const totalFrames = scenes.reduce(
            (sum: number, s: any) => sum + Math.ceil(((s.audioDurationMs || 8000) / 1000) * 30),
            0
          );
          return { durationInFrames: Math.max(totalFrames, 30) };
        }}
      />

      <Composition
        id="DataVisualization"
        component={DataVisualization}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          chartType: 'bar',
          title: 'ANNUAL RAINFALL',
          dataPoints: [
            { label: 'AMAZON', value: 80, color: '#00D25A' },
            { label: 'ANDES', value: 60, color: '#C864FF' },
            { label: 'SAHARA', value: 5, color: '#FFE000' },
            { label: 'ALPS', value: 45, color: '#00DCFF' },
          ],
          subtitle: 'Millimeters per year comparison',
        }}
        calculateMetadata={({ props }) => {
          const p = props as any;
          const durMs = p.audioDurationMs || 6000;
          return { durationInFrames: Math.max(Math.ceil((durMs / 1000) * 30), 30) };
        }}
      />

      <Composition
        id="SplitMap"
        component={SplitMap}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          leftCamera: { latitude: 4.570868, longitude: -74.297333, zoom: 6, label: 'Bogota Basin' },
          rightCamera: { latitude: 40.7128, longitude: -74.006, zoom: 6, label: 'New York Coast' },
          leftTitle: 'THEN',
          rightTitle: 'NOW',
          comparisonLabel: 'COASTLINE CHANGE OVER 50 YEARS',
        }}
        calculateMetadata={({ props }) => {
          const p = props as any;
          const durMs = p.audioDurationMs || 8000;
          return { durationInFrames: Math.max(Math.ceil((durMs / 1000) * 30), 30) };
        }}
      />

      <Composition
        id="HexDataGrid"
        component={HexDataGrid}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: 'ORGANIZED CRIME LANDSCAPE',
          items: [
            { icon: '💀', label: 'HOMICIDES', value: '234/YR', color: '#FF0078' },
            { icon: '🎯', label: 'TRAFFICKING', value: '340T', color: '#FFE000' },
            { icon: '💰', label: 'VALUE', value: '$2.1B', color: '#00D25A' },
            { icon: '🧪', label: 'CHEMICALS', value: '87%', color: '#00DCFF' },
            { icon: '🌿', label: 'CULTIVATION', value: '45K HA', color: '#C864FF' },
            { icon: '⛺', label: 'CAMPS', value: '1,200', color: '#FF8C00' },
          ],
        }}
        calculateMetadata={({ props }) => {
          const p = props as any;
          const durMs = p.audioDurationMs || 8000;
          return { durationInFrames: Math.max(Math.ceil((durMs / 1000) * 30), 30) };
        }}
      />
    </>
  );
};
