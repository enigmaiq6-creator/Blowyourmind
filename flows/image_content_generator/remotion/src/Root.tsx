import { Composition } from 'remotion';
import { Subtitles } from './Subtitles';
import { MapRender } from './MapRender';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Subtitles"
        component={Subtitles}
        durationInFrames={1500}
        fps={25}
        width={1080}
        height={1920}
        defaultProps={{
          words: [
            { text: "BlowYourMind", start: 0, end: 1000 },
            { text: "Mind", start: 1000, end: 2000 },
            { text: "Blowing", start: 2000, end: 3000 }
          ]
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
    </>
  );
};
