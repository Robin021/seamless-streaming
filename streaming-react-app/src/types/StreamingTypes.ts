export const SUPPORTED_LANGUAGE_CODES = ['en-US', 'es-ES'] as const;

export type SupportedLanguageCode = (typeof SUPPORTED_LANGUAGE_CODES)[number];

export type StartStreamingData = {
  inputLang: SupportedLanguageCode;
  outputLang: SupportedLanguageCode;
  outputMode: SupportedOutputMode;
};

interface ServerTranslationDataBase {
  eos: boolean;
  event: string;
  latency?: number;
}

export interface ServerTextData extends ServerTranslationDataBase {
  event: 'translation_text';
  payload: string;
}

export interface ServerSpeechData extends ServerTranslationDataBase {
  event: 'translation_speech';
  payload: Array<number>;
  sample_rate: number;
}

export const OUTPUT_MODALITIES_BASE_VALUES = ['s2t', 's2s'] as const;
export type OutputModalitiesBase =
  (typeof OUTPUT_MODALITIES_BASE_VALUES)[number];

export const DYNAMIC_PARAMS_VALUES = ['expressive'] as const;
export type DynamicParams = (typeof DYNAMIC_PARAMS_VALUES)[number];

export type AgentCapabilities = {
  name: string;
  description: string;
  modalities: Array<OutputModalitiesBase>;
  sourceLangs: Array<string>;
  targetLangs: Array<string>;
  dynamicParams: Array<DynamicParams>;
};

export const SUPPORTED_OUTPUT_MODE_VALUES = ['s2s&t', 's2t', 's2s'] as const;

export type SupportedOutputMode = (typeof SUPPORTED_OUTPUT_MODE_VALUES)[number];

export const SUPPORTED_OUTPUT_MODES: Array<{
  value: (typeof SUPPORTED_OUTPUT_MODE_VALUES)[number];
  label: string;
}> = [
  {value: 's2s&t', label: 'Text & Speech'},
  {value: 's2t', label: 'Text'},
  {value: 's2s', label: 'Speech'},
];

export const SUPPORTED_INPUT_SOURCE_VALUES = [
  'userMedia',
  'displayMedia',
] as const;

export type SupportedInputSource =
  (typeof SUPPORTED_INPUT_SOURCE_VALUES)[number];

export const SUPPORTED_INPUT_SOURCES: Array<{
  value: SupportedInputSource;
  label: string;
}> = [
  {value: 'userMedia', label: 'Microphone'},
  {value: 'displayMedia', label: 'Browser Tab'},
];

export type StartStreamEventConfig = {
  event: 'config';
  rate: number;
  model_name: string;
  // source_language: SupportedLanguageCode;
  debug: boolean;
  async_processing: boolean;
  model_type: SupportedOutputMode;
  buffer_limit: number;
};

export interface BrowserAudioStreamConfig {
  echoCancellation: boolean;
  noiseSuppression: boolean;
}

export interface ServerStateItem {
  activeConnections: number;
  activeTranscoders: number;
}

export type ServerLockObject = {
  name: string | null;
  clientID: string | null;
  isActive: boolean;
};

export type ServerState = ServerStateItem & {
  agentsCapabilities: Array<AgentCapabilities>;
  statusByRoom: {
    [key: string]: {activeConnections: number; activeTranscoders: number};
  };
  totalActiveConnections: number;
  totalActiveTranscoders: number;
  serverLock: ServerLockObject | null;
};

export type ServerExceptionData = {
  message: string;
  timeEpochMs: number;
  // NOTE: This is added on the client
  timeStringClient?: string;
  room?: string;
  member?: string;
  clientID?: string;
};

export type StreamingStatus = 'stopped' | 'running' | 'starting';

export type TranslationSentences = Array<string>;

export type DynamicConfig = {
  // targetLanguage: a 3-letter string representing the desired output language.
  // Supported languages are provided by the agent capabilities config
  targetLanguage: string;

  expressive: boolean | null;
};

export type PartialDynamicConfig = Partial<DynamicConfig>;

export type BaseResponse = {
  status: 'ok' | 'error';
  message: string;
};

export type Roles = 'speaker' | 'listener';

export type JoinRoomConfig = {
  roles: Array<Roles>;
  lockServerName: string | null;
};
