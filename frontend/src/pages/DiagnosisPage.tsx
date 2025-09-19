import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bot, AlertTriangle, ArrowLeft } from 'lucide-react';
import { Sensor } from '@/components/SensorTable';

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

	const diagnosis = `🔍 The sensor detected that it is not installed in a suitable location, as no vibration, temperature, or connectivity data has been recorded in the last hour.

📋 To regularize the installation, please review the sensor installation conditions according to the recommendations below. If necessary, open a support ticket with the Tractian team.

📝 Recommendations:
📍 Check if the distance between the sensor and the gateway is adequate.
🚫 Check if the asset is blocking the sensor; if yes, reposition either the sensor or the gateway.
📦 Check if the sensor or the gateway are enclosed; if yes, remove them from the enclosure.
🔌 Check if the gateway is powered on; if not, turn it on.
💚 Check if the gateway light is green or blinking green; if not, open a support ticket with Tractian.
🏗️ Check if there are metallic obstructions (assets, pipes, walls) between the sensor and the gateway; if yes, reposition either the sensor or the gateway.`;

	return diagnosis;
};

// Mock sensor data (same as in SensorTable)
const mockSensors: Sensor[] = [
	{
		id: '1',
		sensorId: 'SML1627',
		temperature: false,
		vibration: false,
		connectivity: false,
	},
	{
		id: '2',
		sensorId: 'NYS0043',
		temperature: true,
		vibration: true,
		connectivity: true,
	},
	{
		id: '3',
		sensorId: 'KPC3319',
		temperature: true,
		vibration: true,
		connectivity: true,
	},
];

const DiagnosisPage = () => {
	const { sensorId } = useParams<{ sensorId: string }>();
	const navigate = useNavigate();
	const diagnosisTextRef = useRef<HTMLPreElement>(null);
	const [sensor, setSensor] = useState<Sensor | null>(null);
	const [diagnosisState, setDiagnosisState] = useState<{
		displayedText: string;
		isStreaming: boolean;
		isCompleted: boolean;
		isError: boolean;
		errorMessage?: string;
	}>({
		displayedText: '',
		isStreaming: false,
		isCompleted: false,
		isError: false,
	});

	useEffect(() => {
		// Find sensor by sensorId from URL params
		const foundSensor = mockSensors.find((s) => s.sensorId === sensorId);
		if (foundSensor) {
			setSensor(foundSensor);
		}
	}, [sensorId]);

	// Auto-scroll effect when text is streaming
	useEffect(() => {
		if (diagnosisState.isStreaming && diagnosisTextRef.current) {
			diagnosisTextRef.current.scrollIntoView({
				behavior: 'smooth',
				block: 'end',
			});
		}
	}, [diagnosisState.displayedText, diagnosisState.isStreaming]);

	useEffect(() => {
		if (
			sensor &&
			!diagnosisState.isCompleted &&
			!diagnosisState.isStreaming &&
			!diagnosisState.isError
		) {
			setDiagnosisState((prev) => ({
				...prev,
				isStreaming: true,
				isError: false,
			}));

			// Fetch diagnosis from LLM API
			fetchDiagnosisFromLLM(sensor)
				.then((fullText) => {
					let currentIndex = 0;

					const streamText = () => {
						if (currentIndex < fullText.length) {
							setDiagnosisState((prev) => ({
								...prev,
								displayedText: fullText.slice(
									0,
									currentIndex + 1
								),
							}));
							currentIndex++;
							setTimeout(streamText, 10); // Adjust speed here
						} else {
							setDiagnosisState((prev) => ({
								...prev,
								isStreaming: false,
								isCompleted: true,
							}));
						}
					};

					// Start streaming after API response
					setTimeout(streamText, 500);
				})
				.catch((error) => {
					setDiagnosisState((prev) => ({
						...prev,
						isStreaming: false,
						isError: true,
						errorMessage: error.message,
					}));
				});
		}
	}, [
		sensor,
		diagnosisState.isCompleted,
		diagnosisState.isStreaming,
		diagnosisState.isError,
	]);

	if (!sensor) {
		return (
			<div className='min-h-screen bg-gradient-to-br from-background via-secondary/20 to-accent/10 flex items-center justify-center'>
				<Card className='max-w-md mx-auto'>
					<CardContent className='p-6 text-center'>
						<AlertTriangle className='h-12 w-12 text-red-500 mx-auto mb-4' />
						<h2 className='text-xl font-semibold mb-2'>
							Sensor Not Found
						</h2>
						<p className='text-muted-foreground mb-4'>
							The sensor with ID "{sensorId}" could not be found.
						</p>
						<Button onClick={() => navigate('/')}>
							<ArrowLeft className='h-4 w-4 mr-2' />
							Back to Sensors
						</Button>
					</CardContent>
				</Card>
			</div>
		);
	}

	return (
		<div className='min-h-screen bg-gradient-to-br from-background via-secondary/20 to-accent/10'>
			<div className='py-8'>
				<header className='text-center mb-8'>
					<img
						src='/tractian-logo.png'
						alt='Tractian'
						className='w-1/4 mx-auto'
					/>
				</header>

				<div className='w-full max-w-4xl mx-auto p-6'>
					{/* Header with back button */}
					<div className='mb-6'>
						<Button
							variant='outline'
							onClick={() => navigate('/')}
							className='mb-4'
						>
							<ArrowLeft className='h-4 w-4 mr-2' />
							Back to Sensors
						</Button>
					</div>

					{/* Diagnosis Card */}
					<Card className='shadow-[var(--shadow-card)] border-border/50 bg-gradient-to-br from-card to-secondary/20'>
						<CardHeader className='border-b border-border/30 pb-4'>
							<CardTitle className='flex items-center gap-3 text-xl flex-wrap'>
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
								{diagnosisState.isStreaming && (
									<div className='flex items-center gap-1'>
										<div className='w-2 h-2 bg-ai-primary rounded-full animate-pulse'></div>
										<span className='text-sm text-muted-foreground'>
											Connecting to LLM...
										</span>
									</div>
								)}
								{diagnosisState.isError && (
									<div className='flex items-center gap-1'>
										<div className='w-2 h-2 bg-red-500 rounded-full'></div>
										<span className='text-sm text-red-500'>
											Service Error
										</span>
									</div>
								)}
							</CardTitle>
						</CardHeader>

						<CardContent className='space-y-4 pt-4'>
							<div className='bg-gradient-to-r from-secondary/30 to-accent/20 p-4 rounded-lg border border-border/30'>
								<div className='flex items-center gap-2 mb-3'>
									<AlertTriangle className='h-4 w-4 text-status-warning' />
									<span className='font-semibold text-foreground'>
										Diagnostic Report
									</span>
								</div>

								<div className='bg-card/80 rounded-md p-4 border border-border/30 shadow-inner'>
									{diagnosisState.isError ? (
										<div className='text-center py-8'>
											<div className='text-red-500 mb-2'>
												<AlertTriangle className='h-8 w-8 mx-auto' />
											</div>
											<p className='text-red-500 font-semibold mb-2'>
												LLM Service Error
											</p>
											<p className='text-muted-foreground text-sm'>
												{diagnosisState.errorMessage}
											</p>
											<p className='text-muted-foreground text-xs mt-2'>
												Please try again later or
												contact support.
											</p>
										</div>
									) : (
										<pre
											ref={diagnosisTextRef}
											className='whitespace-pre-wrap text-sm text-foreground font-mono leading-relaxed'
										>
											{diagnosisState.displayedText}
											{diagnosisState.isStreaming && (
												<span className='inline-block w-2 h-4 bg-ai-primary animate-pulse ml-1'></span>
											)}
										</pre>
									)}
								</div>
							</div>
						</CardContent>
					</Card>
				</div>
			</div>
		</div>
	);
};

export default DiagnosisPage;
