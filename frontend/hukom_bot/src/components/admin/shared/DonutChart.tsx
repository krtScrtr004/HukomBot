interface DonutChartSegment {
	/** Legend label */
	label: string;
	/** Numeric value for the segment */
	value: number;
	/** Tailwind bg class for the legend dot, e.g. 'bg-primary' */
	color: string;
	/** CSS color value for the conic-gradient, e.g. 'var(--color-primary)' */
	cssColor: string;
}

interface DonutChartProps {
	/** Segments to render in the donut */
	segments: DonutChartSegment[];
	/** Value displayed in the center (auto-calculated from segments if omitted) */
	centerValue?: number;
	/** Label displayed below the center value */
	centerLabel?: string;
	/** Optional className on the outermost wrapper div */
	className?: string;
}

export default function DonutChart({
	segments,
	centerValue,
	centerLabel = 'Total',
	className,
}: DonutChartProps) {
	const total = centerValue ?? segments.reduce((sum, s) => sum + s.value, 0);

	// Compute percentage for each segment
	const segmentData = segments.map((s) => ({
		...s,
		percent: total > 0 ? Math.round((s.value / total) * 100) : 0,
	}));

	// Ensure percentages sum to 100 by adjusting the last segment
	if (total > 0 && segmentData.length > 0) {
		const sumPct = segmentData.reduce((acc, s) => acc + s.percent, 0);
		segmentData[segmentData.length - 1].percent += 100 - sumPct;
	}

	// Build conic-gradient stops
	let conicGradient = 'var(--color-surface-muted)';
	if (total > 0 && segmentData.length > 0) {
		let currentDeg = 0;
		const stops = segmentData.map((s) => {
			const startDeg = currentDeg;
			const endDeg = currentDeg + (s.percent / 100) * 360;
			currentDeg = endDeg;
			return `${s.cssColor} ${startDeg}deg ${endDeg}deg`;
		});
		conicGradient = `conic-gradient(${stops.join(', ')})`;
	}

	return (
		<div className={className}>
			{/* Donut Ring */}
			<div className="my-6 flex items-center justify-center">
				<div
					className="relative h-36 w-36 rounded-full shadow-inner flex items-center justify-center transition-all"
					style={{ background: conicGradient }}
				>
					<div className="h-24 w-24 rounded-full bg-surface shadow-xs flex flex-col items-center justify-center">
						<span className="text-xl font-bold text-text-primary">
							{total.toLocaleString()}
						</span>
						<span className="text-[10px] text-text-muted uppercase font-medium">
							{centerLabel}
						</span>
					</div>
				</div>
			</div>

			{/* Legend List */}
			<div className="space-y-2.5">
				{segmentData.map((seg) => (
					<div key={seg.label} className="flex items-center justify-between text-xs">
						<div className="flex items-center gap-2">
							<span className={`h-2.5 w-2.5 rounded-full ${seg.color}`} />
							<span className="font-medium text-text-secondary">{seg.label}</span>
						</div>
						<div className="flex items-center gap-3">
							<span className="text-text-muted">{seg.percent}%</span>
							<strong className="text-text-primary font-semibold w-10 text-right">
								{seg.value.toLocaleString()}
							</strong>
						</div>
					</div>
				))}
			</div>
		</div>
	);
}

