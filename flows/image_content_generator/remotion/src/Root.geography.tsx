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
            { text: "EnigmaIQ", start: 0, end: 1000 },
            { text: "Inteligencia", start: 1000, end: 2000 },
            { text: "Financiera", start: 2000, end: 3000 }
          ]
        }}
      />
      
      <Composition
        id="MapRender"
        component={MapRender}
        durationInFrames={240} // 8 seconds
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          latitude: 4.570868,
          longitude: -74.297333,
          zoom: 5.2,
          pitch: 45,
          bearing: -10,
          highlightRegion: 'Colombia',
          arrowDirection: 'none',
          floatingLabel: '52.32M Hab.'
        }}
      />
    </>
  );
};
