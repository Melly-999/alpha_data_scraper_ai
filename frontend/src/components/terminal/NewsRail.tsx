import type { NewsItem } from "../../lib/terminalApi";

type NewsRailProps = {
  news: NewsItem[];
};

export function NewsRail({ news }: NewsRailProps) {
  return (
    <aside className="news-rail">
      <div className="panel-header">
        <span>News sentiment</span>
        <span>read-only</span>
      </div>
      <div className="news-list">
        {news.map((item) => (
          <article key={item.id} className="news-item">
            <div className="news-meta">
              <span>{item.source}</span>
              <span>{item.time}</span>
            </div>
            <h3>{item.headline}</h3>
            <div className="news-tags">
              <span>{item.sentiment}</span>
              <span>{item.impact} impact</span>
            </div>
          </article>
        ))}
      </div>
    </aside>
  );
}
