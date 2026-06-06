# ── Stories (Standard Shorts) ──
icg-s-step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1

icg-s-step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2

icg-s-step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3

icg-s-step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4

icg-s-step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5

icg-s-step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6

icg-s-step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7

icg-s-step8:
	poetry run python -m flows.image_content_generator.pipeline.main short step8

icg-s-all:
	poetry run python -m flows.image_content_generator.pipeline.main short all

# ── Geography (3D Map Shorts) ──
icg-g-step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1 --mode geography

icg-g-step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2 --mode geography

icg-g-step2b:
	poetry run python -m flows.image_content_generator.pipeline.main short step2b --mode geography

icg-g-step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3 --mode geography

icg-g-step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4 --mode geography

icg-g-step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5 --mode geography

icg-g-step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6 --mode geography

icg-g-step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7 --mode geography

icg-g-step8:
	poetry run python -m flows.image_content_generator.pipeline.main short step8 --mode geography

icg-g-all:
	poetry run python -m flows.image_content_generator.pipeline.main short all --mode geography

# ── 7 Levels (English) ──
icg-7-step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1 --mode seven_levels

icg-7-step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2 --mode seven_levels

icg-7-step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3 --mode seven_levels

icg-7-step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4 --mode seven_levels

icg-7-step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5 --mode seven_levels

icg-7-step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6 --mode seven_levels

icg-7-step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7 --mode seven_levels

icg-7-step8:
	poetry run python -m flows.image_content_generator.pipeline.main short step8 --mode seven_levels

icg-7-all:
	poetry run python -m flows.image_content_generator.pipeline.main short all --mode seven_levels

# ── Daily Automation ──
daily-mix:
	poetry run python flows/image_content_generator/pipeline/daily_automated_content.py
