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
    </>
  );
};
