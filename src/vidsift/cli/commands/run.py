from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator


def handle_pipeline_run(self, args, config):
    channel_id_list = ["UCo71RUe6DX4w-Vd47rFLXPg", ]

    self.orchestrator = VidsiftOrchestrator(channel_id_list, config=config)

    self.orchestrator.run()
