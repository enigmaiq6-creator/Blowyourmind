import argparse
from enum import Enum
from pathlib import Path

from flows.image_content_generator.pipeline.pipeline import Pipeline
from flows.image_content_generator.pipeline.schemas import VideoOrientation
from tools.common.messenger import Messenger

RESOURCE_BASE = Path("flows/image_content_generator/resource")
LONG_OUT_BASE = Path("flows/image_content_generator/out_long")
SHORT_OUT_BASE = Path("flows/image_content_generator/out_short")


class PipelineStep(str, Enum):
    ALL = "all"
    STEP1 = "step1"
    STEP2 = "step2"
    STEP2B = "step2b"
    STEP3 = "step3"
    STEP4 = "step4"
    STEP5 = "step5"
    STEP5_PRO = "step5_pro"
    STEP6 = "step6"
    STEP7 = "step7"
    STEP8 = "step8"
    STEP8_IMAGE = "step8_image"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("orientation", type=VideoOrientation, choices=list(VideoOrientation))
    parser.add_argument("step", type=PipelineStep, choices=list(PipelineStep))
    parser.add_argument("--avoid", type=str, default="", help="List of topics to avoid")
    parser.add_argument("--mode", type=str, default="standard", choices=["standard", "stickman", "geography"], help="Content generation mode")
    args = parser.parse_args()

    # Determine output base based on orientation
    out_base = SHORT_OUT_BASE if args.orientation == VideoOrientation.SHORT else LONG_OUT_BASE

    pipeline = Pipeline(
        out_base=out_base,
        resource_base=RESOURCE_BASE,
        orientation=args.orientation,
        mode=args.mode
    )

    # Map Enum members to their corresponding pipeline methods
    step_methods = {
        PipelineStep.STEP1: pipeline.step1_generate_story,
        PipelineStep.STEP2: pipeline.step2_generate_images,
        PipelineStep.STEP2B: pipeline.step2b_generate_video_clips,
        PipelineStep.STEP3: pipeline.step3_generate_audios,
        PipelineStep.STEP4: pipeline.step4_generate_videos,
        PipelineStep.STEP5: pipeline.step5_generate_subtitles,
        PipelineStep.STEP5_PRO: pipeline.step5_pro_subtitles,
        PipelineStep.STEP6: pipeline.step6_add_background_music,
        PipelineStep.STEP7: pipeline.step7_rename_final_video,
        PipelineStep.STEP8: pipeline.step8_upload_to_facebook,
        PipelineStep.STEP8_IMAGE: pipeline.step8_upload_image_to_facebook,
    }

    # Note: Step 1 can take an extra_avoid string
    if args.step == PipelineStep.STEP1:
        pipeline.step1_generate_story(extra_avoid=args.avoid)
    elif args.step == PipelineStep.ALL:
        Messenger.info("--- Starting Full Pipeline Run (Steps 1-8) ---")
        pipeline.step1_generate_story(extra_avoid=args.avoid)
        # We run PRO subtitles instead of standard if step is ALL
        steps_to_run = [
            PipelineStep.STEP2, PipelineStep.STEP3, PipelineStep.STEP2B, PipelineStep.STEP4,
            PipelineStep.STEP5_PRO, PipelineStep.STEP6, PipelineStep.STEP7, PipelineStep.STEP8
        ]
        for step in steps_to_run:
            step_methods[step]()
        Messenger.success("Full pipeline cycle completed successfully.")
    else:
        # Run specific step (2-8)
        step_methods[args.step]()


if __name__ == "__main__":
    main()
