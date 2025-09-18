import { useState, useEffect } from 'react';
import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Bot, AlertTriangle } from 'lucide-react';
import { Sensor } from './SensorTable';

interface DiagnosisModalProps {
	isOpen: boolean;
	onClose: () => void;
	sensor: Sensor | null;
}

// Simulate LLM API request for diagnosis
const fetchDiagnosisFromLLM = async (sensor: Sensor): Promise<string> => {
	// Simulate API call delay
	await new Promise((resolve) =>
		setTimeout(resolve, 1000 + Math.random() * 2000)
	);

	// Simulate potential API failure (5% chance)
	if (Math.random() < 0.05) {
		throw new Error('LLM service temporarily unavailable');
	}

	const issues = [];
	if (!sensor.temperature) issues.push('temperature sensor malfunction');
	if (!sensor.vibration) issues.push('vibration sensor disconnected');
	if (!sensor.connectivity) issues.push('network connectivity failure');

	// Simulate different LLM response styles
	const responseStyles = [
		{
			prefix: '🔍 DETECTED ISSUES:',
			tempAdvice:
				'🌡️ TEMPERATURE: Check thermal sensors and calibration. Possible overheating or sensor drift detected.',
			vibAdvice:
				'📳 VIBRATION: Inspect mounting brackets and sensor connections. Abnormal vibration patterns indicate potential mechanical wear.',
			connAdvice:
				'📡 CONNECTIVITY: Network interface requires attention. Check cables, power supply, and communication protocols.',
		},
		{
			prefix: '⚠️ IDENTIFIED PROBLEMS:',
			tempAdvice:
				'🌡️ TEMPERATURE ANALYSIS: Thermal sensor readings indicate potential calibration issues or environmental interference.',
			vibAdvice:
				'📳 VIBRATION ANALYSIS: Mechanical resonance patterns suggest bearing wear or misalignment.',
			connAdvice:
				'📡 CONNECTIVITY ANALYSIS: Communication protocols experiencing intermittent failures.',
		},
		{
			prefix: '🚨 CRITICAL FINDINGS:',
			tempAdvice:
				'🌡️ TEMPERATURE CRITICAL: Sensor drift detected - immediate calibration required.',
			vibAdvice:
				'📳 VIBRATION CRITICAL: Abnormal frequency patterns detected - mechanical inspection urgent.',
			connAdvice:
				'📡 CONNECTIVITY CRITICAL: Network instability - hardware replacement may be necessary.',
		},
	];

	const style =
		responseStyles[Math.floor(Math.random() * responseStyles.length)];

	const diagnosis = `AI Diagnosis for ${sensor.sensorId}:

${style.prefix}
${issues.map((issue) => `• ${issue.toUpperCase()}`).join('\n')}

📊 TECHNICAL ANALYSIS:
Based on sensor data patterns and historical performance metrics, the following recommendations are suggested:

${!sensor.temperature ? style.tempAdvice : ''}
${!sensor.vibration ? style.vibAdvice : ''}
${!sensor.connectivity ? style.connAdvice : ''}

⚡ RECOMMENDED ACTIONS:
1. Schedule immediate maintenance inspection
2. Replace faulty sensors as identified
3. Verify all electrical connections
4. Test system after repairs
5. Monitor for 24-48 hours post-maintenance

🎯 PRIORITY LEVEL: ${issues.length > 1 ? 'HIGH' : 'MEDIUM'}
Estimated repair time: ${issues.length * 2}-${issues.length * 4} hours
Confidence score: ${Math.floor(85 + Math.random() * 15)}%

This diagnosis is generated using advanced AI pattern recognition algorithms and should be verified by qualified technicians.`;

	return diagnosis;
};

export const DiagnosisModal = ({
	isOpen,
	onClose,
	sensor,
}: DiagnosisModalProps) => {
	const [diagnosisStates, setDiagnosisStates] = useState<
		Record<
			string,
			{
				displayedText: string;
				isStreaming: boolean;
				isCompleted: boolean;
				isError: boolean;
				errorMessage?: string;
			}
		>
	>({});

	useEffect(() => {
		if (isOpen && sensor) {
			const sensorId = sensor.id;

			// Initialize state for this sensor if it doesn't exist
			if (!diagnosisStates[sensorId]) {
				setDiagnosisStates((prev) => ({
					...prev,
					[sensorId]: {
						displayedText: '',
						isStreaming: false,
						isCompleted: false,
						isError: false,
					},
				}));
			}

			const currentState = diagnosisStates[sensorId];

			// Only start streaming if this sensor hasn't been diagnosed yet
			if (
				!currentState?.isCompleted &&
				!currentState?.isStreaming &&
				!currentState?.isError
			) {
				setDiagnosisStates((prev) => ({
					...prev,
					[sensorId]: {
						...prev[sensorId],
						isStreaming: true,
						isError: false,
					},
				}));

				// Fetch diagnosis from LLM API
				fetchDiagnosisFromLLM(sensor)
					.then((fullText) => {
						let currentIndex = 0;

						const streamText = () => {
							if (currentIndex < fullText.length) {
								setDiagnosisStates((prev) => ({
									...prev,
									[sensorId]: {
										...prev[sensorId],
										displayedText: fullText.slice(
											0,
											currentIndex + 1
										),
									},
								}));
								currentIndex++;
								setTimeout(streamText, 30); // Adjust speed here
							} else {
								setDiagnosisStates((prev) => ({
									...prev,
									[sensorId]: {
										...prev[sensorId],
										isStreaming: false,
										isCompleted: true,
									},
								}));
							}
						};

						// Start streaming after API response
						setTimeout(streamText, 500);
					})
					.catch((error) => {
						setDiagnosisStates((prev) => ({
							...prev,
							[sensorId]: {
								...prev[sensorId],
								isStreaming: false,
								isError: true,
								errorMessage: error.message,
							},
						}));
					});
			}
		}
	}, [isOpen, sensor, diagnosisStates]);

	if (!sensor) return null;

	const currentState = diagnosisStates[sensor.id];
	const displayedText = currentState?.displayedText || '';
	const isStreaming = currentState?.isStreaming || false;
	const isError = currentState?.isError || false;
	const errorMessage = currentState?.errorMessage || '';

	return (
		<Dialog open={isOpen} onOpenChange={onClose}>
			<DialogContent className='max-w-2xl max-h-[80vh] overflow-y-auto bg-gradient-to-br from-card to-secondary/10 border-border/50 shadow-[var(--shadow-primary)]'>
				<DialogHeader className='border-b border-border/30 pb-4'>
					<DialogTitle className='flex items-center gap-3 text-xl'>
						<div className='p-2 rounded-lg bg-ai-primary/10 border border-ai-primary/20'>
							<Bot className='h-5 w-5 text-ai-primary' />
						</div>
						AI Diagnosis
						<Badge
							variant='outline'
							className='bg-primary/10 border-primary/30 text-primary'
						>
							{sensor.sensorId}
						</Badge>
						{isStreaming && (
							<div className='flex items-center gap-1'>
								<div className='w-2 h-2 bg-ai-primary rounded-full animate-pulse'></div>
								<span className='text-sm text-muted-foreground'>
									Connecting to LLM...
								</span>
							</div>
						)}
						{isError && (
							<div className='flex items-center gap-1'>
								<div className='w-2 h-2 bg-red-500 rounded-full'></div>
								<span className='text-sm text-red-500'>
									Service Error
								</span>
							</div>
						)}
					</DialogTitle>
				</DialogHeader>

				<div className='space-y-4 pt-4'>
					<div className='bg-gradient-to-r from-secondary/30 to-accent/20 p-4 rounded-lg border border-border/30'>
						<div className='flex items-center gap-2 mb-3'>
							<AlertTriangle className='h-4 w-4 text-status-warning' />
							<span className='font-semibold text-foreground'>
								Diagnostic Report
							</span>
						</div>

						<div className='bg-card/80 rounded-md p-4 border border-border/30 shadow-inner'>
							{isError ? (
								<div className='text-center py-8'>
									<div className='text-red-500 mb-2'>
										<AlertTriangle className='h-8 w-8 mx-auto' />
									</div>
									<p className='text-red-500 font-semibold mb-2'>
										LLM Service Error
									</p>
									<p className='text-muted-foreground text-sm'>
										{errorMessage}
									</p>
									<p className='text-muted-foreground text-xs mt-2'>
										Please try again later or contact
										support.
									</p>
								</div>
							) : (
								<pre className='whitespace-pre-wrap text-sm text-foreground font-mono leading-relaxed'>
									{displayedText}
									{isStreaming && (
										<span className='inline-block w-2 h-4 bg-ai-primary animate-pulse ml-1'></span>
									)}
								</pre>
							)}
						</div>
					</div>
				</div>
			</DialogContent>
		</Dialog>
	);
};
