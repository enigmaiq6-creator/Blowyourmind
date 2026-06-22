# ── Standard (Curiosity Reels) ──
icg-s-step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1 --mode standard

icg-s-step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2 --mode standard

icg-s-step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3 --mode standard

icg-s-step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4 --mode standard

icg-s-step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5 --mode standard

icg-s-step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6 --mode standard

icg-s-step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7 --mode standard

icg-s-step8:

	poetry run python -m flows.image_content_generator.pipeline.main short step8 --mode standard

icg-s-all:
	poetry run python -m flows.image_content_generator.pipeline.main short all --mode standard

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

# ── Finance (English Listicle) ──
icg-f-step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1 --mode finance

icg-f-step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2 --mode finance

icg-f-step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3 --mode finance

icg-f-step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4 --mode finance

icg-f-step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5 --mode finance

icg-f-step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6 --mode finance

icg-f-step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7 --mode finance

icg-f-step8:
	poetry run python -m flows.image_content_generator.pipeline.main short step8 --mode finance

icg-f-all:
	poetry run python -m flows.image_content_generator.pipeline.main short all --mode finance

# ── What If (Alternate Geography) ──
icg-w-step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1 --mode what_if

icg-w-step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2 --mode what_if

icg-w-step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3 --mode what_if

icg-w-step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4 --mode what_if

icg-w-step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5 --mode what_if

icg-w-step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6 --mode what_if

icg-w-step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7 --mode what_if

icg-w-step8:
	poetry run python -m flows.image_content_generator.pipeline.main short step8 --mode what_if

icg-w-all:
	poetry run python -m flows.image_content_generator.pipeline.main short all --mode what_if
