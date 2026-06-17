from vidsift.ingestion.metadata_collector import MetadataCollector
from vidsift.models.video import Video
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator


def handle_process(self, args):
    metadata_collector = MetadataCollector()
    orchestrator = VidsiftOrchestrator(
        channel_id_list=[""],
        config=self.config
    )
    vid: Video = metadata_collector.fetch_metadata(args.url)
    if args.download:
        orchestrator.download(
            vid=vid
        )
    else:
        transcript = orchestrator.fetch_transcript(
            vid=vid
        )
        if args.summarize:
            orchestrator.summarize(
                vid=vid,
                transcript=transcript
            )
        elif args.fetch_transcript:
            print(transcript)
        else:
            validation_result = orchestrator.validate_video(
                vid=vid,
                raw_transcript=transcript
            )
            orchestrator.take_action_on_video(
                vid=vid,
                video_validation_result=validation_result,
                transcript=transcript
            )
