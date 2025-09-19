import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { X, Brain, Check, Thermometer, Wifi, Zap } from 'lucide-react';
import { useIsMobile } from '@/hooks/use-mobile';

export interface Sensor {
	id: string;
	sensorId: string;
	temperature: boolean;
	vibration: boolean;
	connectivity: boolean;
}

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

// API function to fetch sensors data
const fetchSensors = async (sensorIds?: string[]): Promise<Sensor[]> => {
	// TODO: Replace with actual API call
	// const response = await fetch(`/api/sensors${sensorIds ? `?ids=${sensorIds.join(',')}` : ''}`);
	// return response.json();

	// For now, return mocked data
	return new Promise((resolve) => {
		setTimeout(() => {
			if (sensorIds && sensorIds.length > 0) {
				// If URL params are provided, filter sensors by those IDs
				const filteredSensors = mockSensors.filter((sensor) =>
					sensorIds.includes(sensor.sensorId)
				);
				// Return filtered sensors (even if empty array - no fallback to all sensors)
				resolve(filteredSensors);
			} else {
				// If no URL params, return all mock sensors
				resolve(mockSensors);
			}
		}, 100); // Simulate network delay
	});
};

// Mobile Card Component
const SensorCard = ({
	sensor,
	onDiagnose,
}: {
	sensor: Sensor;
	onDiagnose: (sensor: Sensor) => void;
}) => {
	const hasIssues =
		!sensor.temperature || !sensor.vibration || !sensor.connectivity;

	const getStatusIcon = (status: boolean) => {
		return status ? (
			<Check className='h-4 w-4 text-green-600' />
		) : (
			<X className='h-4 w-4 text-red-600' />
		);
	};

	return (
		<Card className='shadow-[var(--shadow-card)] border-border/50 bg-gradient-to-br from-card to-secondary/20'>
			<CardHeader className='pb-3'>
				<div className='flex items-center justify-between'>
					<Badge
						variant='outline'
						className='font-mono text-sm bg-muted/50 border-border/50'
					>
						{sensor.sensorId}
					</Badge>
					<div
						className={`w-2 h-2 rounded-full ${
							hasIssues ? 'bg-red-500' : 'bg-green-500'
						}`}
					/>
				</div>
			</CardHeader>
			<CardContent className='pt-0'>
				<div className='space-y-3'>
					{/* Temperature Status */}
					<div className='flex items-center justify-between'>
						<div className='flex items-center gap-2'>
							<Thermometer className='h-4 w-4 text-muted-foreground' />
							<span className='text-sm font-medium'>
								Temperature
							</span>
						</div>
						{getStatusIcon(sensor.temperature)}
					</div>

					{/* Vibration Status */}
					<div className='flex items-center justify-between'>
						<div className='flex items-center gap-2'>
							<Zap className='h-4 w-4 text-muted-foreground' />
							<span className='text-sm font-medium'>
								Vibration
							</span>
						</div>
						{getStatusIcon(sensor.vibration)}
					</div>

					{/* Connectivity Status */}
					<div className='flex items-center justify-between'>
						<div className='flex items-center gap-2'>
							<Wifi className='h-4 w-4 text-muted-foreground' />
							<span className='text-sm font-medium'>
								Connectivity
							</span>
						</div>
						{getStatusIcon(sensor.connectivity)}
					</div>
				</div>

				{/* Action Button */}
				<div className='mt-4 pt-3 border-t border-border/50'>
					<Button
						size='sm'
						disabled={!hasIssues}
						onClick={() => onDiagnose(sensor)}
						className='w-full transition-all duration-200 disabled:cursor-not-allowed'
					>
						<Brain className='h-4 w-4 mr-2' />
						AI Diagnose
					</Button>
				</div>
			</CardContent>
		</Card>
	);
};

export const SensorTable = () => {
	const navigate = useNavigate();
	const [sensors, setSensors] = useState<Sensor[]>([]);
	const [loading, setLoading] = useState(true);
	const isMobile = useIsMobile();

	useEffect(() => {
		const loadSensors = async () => {
			setLoading(true);
			try {
				const urlParams = new URLSearchParams(window.location.search);
				const sensorIds = urlParams.getAll('sensorId');

				let sensorIdsArray: string[] | undefined;
				if (sensorIds && sensorIds.length > 0) {
					sensorIdsArray = sensorIds.map((id) => id.trim());
				}

				const fetchedSensors = await fetchSensors(sensorIdsArray);
				setSensors(fetchedSensors);
			} catch (error) {
				console.error('Failed to fetch sensors:', error);
				setSensors(mockSensors); // Fallback to mock data on error
			} finally {
				setLoading(false);
			}
		};

		loadSensors();
	}, []);

	const hasIssues = (sensor: Sensor): boolean => {
		return !sensor.temperature || !sensor.vibration || !sensor.connectivity;
	};

	const getStatusIcon = (status: boolean) => {
		return status ? (
			<Check className='h-5 w-5 text-status-healthy' />
		) : (
			<X className='h-5 w-5 text-status-error' />
		);
	};

	const handleDiagnose = (sensor: Sensor) => {
		navigate(`/diagnosis/${sensor.sensorId}`);
	};

	if (loading) {
		return (
			<div className='w-full max-w-6xl mx-auto p-6'>
				<Card className='shadow-[var(--shadow-card)] border-border/50 bg-gradient-to-br from-card to-secondary/20'>
					<CardContent className='p-6'>
						<div className='flex items-center justify-center h-32'>
							<div className='text-muted-foreground'>
								Loading sensors...
							</div>
						</div>
					</CardContent>
				</Card>
			</div>
		);
	}

	return (
		<div className='w-full max-w-4xl mx-auto p-6'>
			{isMobile ? (
				// Mobile Card Layout
				<div className='space-y-4'>
					<Card className='shadow-[var(--shadow-card)] border-border/50 bg-gradient-to-br from-card to-secondary/20'>
						<CardHeader className='border-b border-border/50 bg-gradient-to-r from-primary/5 to-secondary/30'>
							<CardTitle className='text-xl font-bold text-foreground flex items-center gap-2'>
								<div className='w-3 h-3 rounded-full bg-gradient-to-r from-primary to-primary/70 shadow-[var(--shadow-glow)]'></div>
								Sensor Status
							</CardTitle>
						</CardHeader>
					</Card>
					<div className='space-y-3'>
						{sensors.map((sensor) => (
							<SensorCard
								key={sensor.id}
								sensor={sensor}
								onDiagnose={handleDiagnose}
							/>
						))}
					</div>
				</div>
			) : (
				// Desktop Table Layout
				<Card className='shadow-[var(--shadow-card)] border-border/50 bg-gradient-to-br from-card to-secondary/20'>
					<CardHeader className='border-b border-border/50 bg-gradient-to-r from-primary/5 to-secondary/30'>
						<CardTitle className='text-2xl font-bold text-foreground flex items-center gap-2'>
							<div className='w-3 h-3 rounded-full bg-gradient-to-r from-primary to-primary/70 shadow-[var(--shadow-glow)]'></div>
							Sensor Status
						</CardTitle>
					</CardHeader>
					<CardContent className='p-6'>
						<Table>
							<TableHeader>
								<TableRow className='border-border/50 hover:bg-secondary/30'>
									<TableHead className='font-semibold text-foreground'>
										Sensor ID
									</TableHead>
									<TableHead className='font-semibold text-foreground text-center'>
										Temperature
									</TableHead>
									<TableHead className='font-semibold text-foreground text-center'>
										Vibration
									</TableHead>
									<TableHead className='font-semibold text-foreground text-center'>
										Connectivity
									</TableHead>
									<TableHead className='font-semibold text-foreground text-center'>
										Actions
									</TableHead>
								</TableRow>
							</TableHeader>
							<TableBody>
								{sensors.map((sensor) => (
									<TableRow
										key={sensor.id}
										className='border-border/50 hover:bg-gradient-to-r hover:from-secondary/20 hover:to-accent/10 transition-all duration-200'
									>
										<TableCell>
											<Badge
												variant='outline'
												className='font-mono text-xs bg-muted/50 border-border/50'
											>
												{sensor.sensorId}
											</Badge>
										</TableCell>
										<TableCell className='text-center'>
											<div className='flex justify-center'>
												{getStatusIcon(
													sensor.temperature
												)}
											</div>
										</TableCell>
										<TableCell className='text-center'>
											<div className='flex justify-center'>
												{getStatusIcon(
													sensor.vibration
												)}
											</div>
										</TableCell>
										<TableCell className='text-center'>
											<div className='flex justify-center'>
												{getStatusIcon(
													sensor.connectivity
												)}
											</div>
										</TableCell>
										<TableCell className='text-center'>
											<div className='flex justify-center'>
												<Button
													size='sm'
													disabled={
														!hasIssues(sensor)
													}
													onClick={() =>
														handleDiagnose(sensor)
													}
													className='transition-all duration-200 disabled:cursor-not-allowed'
												>
													<Brain className='h-4 w-4' />
													AI Diagnose
												</Button>
											</div>
										</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</CardContent>
				</Card>
			)}
		</div>
	);
};
