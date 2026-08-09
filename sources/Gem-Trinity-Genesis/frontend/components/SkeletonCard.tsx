

export default function SkeletonCard() {
    return (
        <div className="w-full h-64 rounded-2xl p-6 bg-card border border-border/50 shadow-sm relative overflow-hidden">
            {/* Header Skeleton */}
            <div className="flex items-start justify-between mb-8">
                <div className="w-12 h-12 rounded-xl bg-muted/50 animate-pulse" />
                <div className="w-20 h-6 rounded-full bg-muted/30 animate-pulse" />
            </div>

            {/* Content Skeleton */}
            <div className="space-y-3">
                <div className="h-6 w-3/4 bg-muted/50 rounded-md animate-pulse" />
                <div className="h-4 w-1/2 bg-muted/30 rounded-md animate-pulse" />
            </div>

            {/* Footer Skeleton */}
            <div className="absolute bottom-6 left-6 right-6">
                <div className="h-2 w-full bg-muted/20 rounded-full overflow-hidden">
                    <div className="h-full w-full animate-shimmer bg-gradient-to-r from-transparent via-white/30 to-transparent bg-[length:200%_100%]" />
                </div>
            </div>
        </div>
    );
}
