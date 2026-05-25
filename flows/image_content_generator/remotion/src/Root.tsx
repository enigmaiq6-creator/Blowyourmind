import { Composition } from 'remotion';
import { Subtitles } from './Subtitles';

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
    </>
  );
};
