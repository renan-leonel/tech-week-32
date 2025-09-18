import { SensorTable } from '@/components/SensorTable';

const Index = () => {
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

				<SensorTable />
			</div>
		</div>
	);
};

export default Index;
