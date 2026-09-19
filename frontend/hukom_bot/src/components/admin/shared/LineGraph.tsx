interface LineGraphDataPoint {
	label: string;
	value: number;
}

interface LineGraphProps {
	/** Data points to plot */
	data: LineGraphDataPoint[];
	/** Accessible aria-label for the SVG element */
	ariaLabel?: string;
	/** Unique SVG gradient ID to avoid collisions when multiple LineGraphs render on the same page */
	gradientId?: string;
	/** Number of Y-axis tick divisions: 3 = top/mid/bottom, 4 = top/⅔/⅓/bottom. Default: 4 */
	yAxisDivisions?: 3 | 4;
	/** SVG viewBox width. Default: 800 */
	viewBoxWidth?: number;
	/** SVG viewBox height. Default: 160 */
	viewBoxHeight?: number;
	/** Stroke color CSS value. Default: 'var(--color-primary)' */
	strokeColor?: string;
	/** Container height class. Default: 'h-48' */
	heightClass?: string;
	/** Optional className on the outermost wrapper div */
	className?: string;
}

export default function LineGraph({
	data,
	ariaLabel = 'Line graph',
	gradientId = 'lineGraphGradient',
	yAxisDivisions = 4,
	viewBoxWidth = 800,
	viewBoxHeight = 160,
	strokeColor = 'var(--color-primary)',
	heightClass = 'h-48',
	className,
}: LineGraphProps) {
	const maxValue = Math.max(...data.map((d) => d.value), 1);

	// Compute Y-axis padding: the line sits within (viewBoxHeight - topPad) to viewBoxHeight
	const topPad = viewBoxHeight - Math.round(viewBoxHeight * 0.875);
	const plotRange = viewBoxHeight - topPad;

	const toY = (value: number) => viewBoxHeight - (value / maxValue) * plotRange;
	const toX = (index: number) => (index / Math.max(data.length - 1, 1)) * viewBoxWidth;

	// Build Y-axis tick labels based on division count
	const yTicks: { position: string; value: string; translate: string }[] = [];

	if (yAxisDivisions === 4) {
		yTicks.push(
			{ position: 'top-0', value: maxValue.toLocaleString(), translate: '-translate-y-1/2' },
			{ position: 'top-1/3', value: Math.round((maxValue * 2) / 3).toLocaleString(), translate: '-translate-y-1/2' },
			{ position: 'top-2/3', value: Math.round(maxValue / 3).toLocaleString(), translate: '-translate-y-1/2' },
			{ position: 'bottom-6', value: '0', translate: 'translate-y-1/2' },
		);
	} else {
		yTicks.push(
			{ position: 'top-0', value: maxValue.toLocaleString(), translate: '-translate-y-1/2' },
			{ position: 'top-1/2', value: Math.round(maxValue / 2).toLocaleString(), translate: '-translate-y-1/2' },
			{ position: 'bottom-6', value: '0', translate: 'translate-y-1/2' },
		);
	}

	// Grid lines
	const gridLines: { position: string; style: string }[] = [];

	if (yAxisDivisions === 4) {
		gridLines.push(
			{ position: 'top-0', style: 'border-t border-border/40' },
			{ position: 'top-1/3', style: 'border-t border-border/30 border-dashed' },
			{ position: 'top-2/3', style: 'border-t border-border/30 border-dashed' },
			{ position: 'bottom-6', style: 'border-t border-border' },
		);
	} else {
		gridLines.push(
			{ position: 'top-0', style: 'border-t border-border' },
			{ position: 'top-1/2', style: 'border-t border-border/60 border-dashed' },
			{ position: 'bottom-6', style: 'border-t border-border' },
		);
	}

	// SVG points string
	const pointsStr = data.map((d, i) => `${toX(i)},${toY(d.value)}`).join(' ');
	const polygonPoints = `0,${viewBoxHeight} ${pointsStr} ${viewBoxWidth},${viewBoxHeight}`;

	return (
		<div className={className}>
			<div className={`relative ${heightClass} pl-10 pr-2`}>
				{/* Y-Axis Scale Tick Labels */}
				{yTicks.map((tick) => (
					<div
						key={tick.position}
						className={`absolute left-0 ${tick.position} w-8 text-right text-[10px] text-text-muted font-mono leading-none ${tick.translate}`}
					>
						{tick.value}
					</div>
				))}

				{/* Background Grid Lines */}
				{gridLines.map((line) => (
					<div
						key={line.position}
						className={`absolute left-10 right-2 ${line.position} ${line.style}`}
					/>
				))}

				{/* SVG Plot */}
				<div className="absolute left-10 right-2 bottom-6 top-2">
					<svg
						viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
						preserveAspectRatio="none"
						className="h-full w-full overflow-visible"
						role="img"
						aria-label={ariaLabel}
					>
						<defs>
							<linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
								<stop offset="0%" stopColor={strokeColor} stopOpacity="0.35" />
								<stop offset="100%" stopColor={strokeColor} stopOpacity="0.0" />
							</linearGradient>
						</defs>

						{/* Gradient Area Fill */}
						<polygon fill={`url(#${gradientId})`} points={polygonPoints} />

						{/* Line Stroke */}
						<polyline
							fill="none"
							stroke={strokeColor}
							strokeWidth="2"
							strokeLinecap="round"
							strokeLinejoin="round"
							points={pointsStr}
						/>

						{/* Data Point Circles */}
						{data.map((d, i) => (
							<g key={d.label} className="group cursor-pointer">
								<circle
									cx={toX(i)}
									cy={toY(d.value)}
									r="1"
									className="fill-surface stroke-primary transition-all group-hover:r-7"
									strokeWidth="3"
								/>
								<title>{`${d.label}: ${d.value.toLocaleString()}`}</title>
							</g>
						))}
					</svg>
				</div>

				{/* X-Axis Labels */}
				<div className="absolute left-10 right-2 bottom-0 flex justify-between text-[11px] text-text-muted font-medium">
					{data.map((d) => (
						<span key={d.label}>{d.label}</span>
					))}
				</div>
			</div>
		</div>
	);
}

