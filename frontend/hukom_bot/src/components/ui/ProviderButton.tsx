interface ProviderButtonProp {
	id: string;
	title: string;
	link: string;
	imgSrc: string;
}

export default function ProviderButton({ id, title, link, imgSrc }: ProviderButtonProp) {
	return (
		<button id={id} className="w-full py-2 bg-background border border-primary rounded-sm flex items-center justify-center text-text-primary cursor-pointer transition-colors hover:bg-primary hover:text-background">
			<a href={link} className="inline-flex items-center justify-center gap-2 ">
				<img
					src={imgSrc}
					className="h-8 font-bold"
					alt={`Continue with ${title}`}
					title={`Continue with ${title}`}
				/>
				<p>Continue with {title}</p>
			</a>
		</button>
	);
}