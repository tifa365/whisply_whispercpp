import click
from pathlib import Path
from whisply import little_helper, transcription


@click.command(no_args_is_help=True)
@click.option('--files', type=click.Path(file_okay=True, dir_okay=True), help='Path to file, folder, URL or .list to process.')
@click.option('--output_dir', default='./transcriptions', type=click.Path(file_okay=False, dir_okay=True), 
              help='Folder where transcripts should be saved. Default: "./transcriptions".')
@click.option('--device', default='cpu', type=click.Choice(['cpu', 'gpu', 'mps'], case_sensitive=False), 
              help='Select the computation device: CPU, GPU (nvidia CUDA), or MPS (Mac M1-M3).')
@click.option('--model', type=str, default='large-v2', 
              help='Select the whisper model to use (Default: large-v2). Refers to whisper model size: https://huggingface.co/collections/openai')
@click.option('--lang', type=str, default=None, 
              help='Specifies the language of the file your providing (en, de, fr ... Default: auto-detection).')
@click.option('--annotate', default=False, is_flag=True, 
              help='Enable speaker detection to identify and annotate different speakers. Creates .rttm file.')
@click.option('--hf_token', type=str, default=None, help='HuggingFace Access token required for speaker detection.')
@click.option('--translate', default=False, is_flag=True, help='Translate transcription to English.')
@click.option('--subtitle', default=False, is_flag=True, help='Create .srt and .webvtt subtitles from the transcription.')
@click.option('--sub_length', default=None, type=int, help="""Subtitle length in words for each subtitle block (Default: 5);
              e.g. "10" produces subtitles where each individual subtitle block covers exactly 10 words.""")
@click.option('--config', type=click.Path(exists=True, file_okay=True, dir_okay=False), help='Path to configuration file.')
@click.option('--filetypes', default=False, is_flag=True, help='List supported audio and video file types.')
@click.option('--verbose', default=False, is_flag=True, help='Print text chunks during transcription.')
def main(**kwargs):
    """
    WHISPLY 🤫 Transcribe, translate, annotate and subtitle audio and video files with OpenAI's Whisper ... fast!
    """
    # Load configuration from config.json if provided
    if kwargs['config']:
        config_data = little_helper.load_config(Path(kwargs['config']))
        kwargs['files'] = kwargs['files'] or config_data.get('files')
        kwargs['output_dir'] = config_data.get('output_dir') if config_data.get('output_dir') is not None else kwargs['output_dir']
        kwargs['device'] = config_data.get('device', kwargs['device'])
        kwargs['model'] = config_data.get('model', kwargs['model'])
        kwargs['lang'] = config_data.get('lang', kwargs['lang'])
        kwargs['annotate'] = config_data.get('annotate', kwargs['annotate'])
        kwargs['translate'] = config_data.get('translate', kwargs['translate'])
        kwargs['hf_token'] = config_data.get('hf_token', kwargs['hf_token'])
        kwargs['subtitle'] = config_data.get('subtitle', kwargs['subtitle'])
        kwargs['sub_length'] = config_data.get('sub_length', kwargs['sub_length'])
        kwargs['verbose'] = config_data.get('verbose', kwargs['verbose'])

    # Check if speaker detection is enabled but no HuggingFace token is provided
    if kwargs['annotate'] and not kwargs['hf_token']:
        click.echo('---> Speaker diarization is enabled but no HuggingFace access token is provided.')
        return 
    
    if kwargs['filetypes']:
        click.echo(f"{' '.join(transcription.TranscriptionHandler().file_formats)}")
        return

    # Instantiate TranscriptionHandler
    service = transcription.TranscriptionHandler(base_dir=kwargs['output_dir'],
                                                 device='cuda:0' if kwargs['device'] == 'gpu' else kwargs['device'],
                                                 model=kwargs['model'],
                                                 file_language=kwargs['lang'], 
                                                 detect_speakers=kwargs['annotate'], 
                                                 translate=kwargs['translate'],
                                                 hf_token=kwargs['hf_token'], 
                                                 subtitle=kwargs['subtitle'],
                                                 sub_length=kwargs['sub_length'],
                                                 verbose=kwargs['verbose'])
    # Process files
    service.process_files(kwargs['files'])

if __name__ == '__main__':
    main()
