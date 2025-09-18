import React from 'react';

const PdfViewer: React.FC = () => {
	return (
		<div className='min-h-screen bg-gray-50 p-4'>
			<div className='max-w-6xl mx-auto'>
				<h1 className='text-2xl font-bold text-gray-800 mb-6'>
					Pontos de Instalação
				</h1>
				<div className='bg-white rounded-lg shadow-lg overflow-hidden'>
					<iframe
						src='/PontosdeInstalação.pdf'
						width='100%'
						height='800px'
						className='border-0'
						title='Pontos de Instalação PDF'
					/>
				</div>
				<div className='mt-4 text-center'>
					<a
						href='/PontosdeInstalação.pdf'
						target='_blank'
						rel='noopener noreferrer'
						className='inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors'
					>
						Abrir PDF em nova aba
					</a>
				</div>
			</div>
		</div>
	);
};

export default PdfViewer;
