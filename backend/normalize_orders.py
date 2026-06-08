"""
One-time script to normalize all API orders in the database.
Ensures all APIs have sequential order numbers starting from 1.
"""

from backend.database import get_session, close_session, API, Section
from backend.db_helpers import normalize_api_orders


def normalize_all_orders():
    """Normalize orders for all APIs in all sections."""
    session = get_session()
    try:
        # Get all sections
        sections = session.query(Section).all()

        print(f"🔄 Normalizing API orders for {len(sections)} sections...")

        for section in sections:
            # Get API count for this section
            api_count = session.query(API).filter_by(section_id=section.id).count()

            if api_count > 0:
                print(f"  📁 {section.name}: {api_count} APIs")
                normalize_api_orders(section.id, session)

        session.commit()
        print("✅ All API orders normalized successfully!")

        # Verify results
        print("\n📊 Verification:")
        for section in sections:
            apis = session.query(API).filter_by(section_id=section.id).order_by(API.order).all()
            if apis:
                orders = [api.order for api in apis]
                print(f"  {section.name}: Orders = {orders}")

    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        close_session(session)


if __name__ == '__main__':
    normalize_all_orders()
